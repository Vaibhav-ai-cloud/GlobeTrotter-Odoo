from odoo.tests.common import TransactionCase


class TestGlobeTrotterBudget(TransactionCase):

    def setUp(self):
        super().setUp()

        self.Trip = self.env["globetrotter.trip"]
        self.Budget = self.env["globetrotter.budget"]
        self.Expense = self.env["globetrotter.expense"]
        self.Recommendation = self.env[
            "globetrotter.recommendation"
        ]

        self.trip = self.Trip.create(
            {
                "name": "Test Trip",
                "user_id": self.env.user.id,
            }
        )

        self.budget = self.Budget.create(
            {
                "name": "Test Budget",
                "trip_id": self.trip.id,
                "total_budget": 20000.0,
                "transport_budget": 4000.0,
                "accommodation_budget": 7000.0,
                "food_budget": 3000.0,
                "activity_budget": 2000.0,
                "other_budget": 1000.0,
            }
        )

    def test_planned_budget_total(self):
        self.assertEqual(
            self.budget.planned_total,
            17000.0,
        )

        self.assertEqual(
            self.budget.remaining_budget,
            3000.0,
        )

        self.assertFalse(
            self.budget.is_over_budget,
        )

    def test_actual_expense_calculation(self):
        self.Expense.create(
            {
                "name": "Hotel Payment",
                "trip_id": self.trip.id,
                "budget_id": self.budget.id,
                "category": "accommodation",
                "amount": 7500.0,
                "is_planned": False,
            }
        )

        self.Expense.create(
            {
                "name": "Food Payment",
                "trip_id": self.trip.id,
                "budget_id": self.budget.id,
                "category": "food",
                "amount": 1200.0,
                "is_planned": False,
            }
        )

        self.budget.invalidate_recordset()

        self.assertEqual(
            self.budget.actual_spent,
            8700.0,
        )

        self.assertEqual(
            self.budget.actual_accommodation,
            7500.0,
        )

        self.assertEqual(
            self.budget.actual_food,
            1200.0,
        )

        self.assertEqual(
            self.budget.actual_remaining,
            11300.0,
        )

    def test_planned_expense_not_counted_as_actual(self):
        self.Expense.create(
            {
                "name": "Planned Taxi",
                "trip_id": self.trip.id,
                "budget_id": self.budget.id,
                "category": "transport",
                "amount": 1000.0,
                "is_planned": True,
            }
        )

        self.budget.invalidate_recordset()

        self.assertEqual(
            self.budget.actual_spent,
            0.0,
        )

    def test_over_budget_detection(self):
        self.Expense.create(
            {
                "name": "Large Expense",
                "trip_id": self.trip.id,
                "budget_id": self.budget.id,
                "category": "other",
                "amount": 22000.0,
                "is_planned": False,
            }
        )

        self.budget.invalidate_recordset()

        self.assertTrue(
            self.budget.is_actual_over_budget,
        )

        self.assertEqual(
            self.budget.actual_remaining,
            -2000.0,
        )

    def test_budget_recommendation_generation(self):
        self.Expense.create(
            {
                "name": "Expensive Stay",
                "trip_id": self.trip.id,
                "budget_id": self.budget.id,
                "category": "accommodation",
                "amount": 9000.0,
                "is_planned": False,
            }
        )

        self.budget.invalidate_recordset()

        recommendations = (
            self.Recommendation
            .generate_budget_recommendations(
                self.trip.id
            )
        )

        self.assertTrue(
            recommendations,
        )

        self.assertTrue(
            any(
                recommendation.recommendation_type
                == "budget"
                for recommendation in recommendations
            )
        )