from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


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


        def test_negative_budget_not_allowed(self):
            with self.assertRaises(ValidationError):
                self.Budget.create(
                    {
                        "name": "Invalid Budget",
                        "trip_id": self.trip.id,
                        "total_budget": -1000.0,
                    }
                )


        def test_zero_or_negative_expense_not_allowed(self):
            with self.assertRaises(ValidationError):
                self.Expense.create(
                    {
                        "name": "Invalid Expense",
                        "trip_id": self.trip.id,
                        "budget_id": self.budget.id,
                        "category": "food",
                        "amount": 0.0,
                        "is_planned": False,
                    }
                )


        def test_expense_inherits_budget_trip_and_currency(self):
            expense = self.Expense.create(
                {
                    "name": "Taxi",
                    "budget_id": self.budget.id,
                    "category": "transport",
                    "amount": 500.0,
                    "is_planned": False,
                }
            )

            self.assertEqual(
                expense.trip_id,
                self.budget.trip_id,
            )

            self.assertEqual(
                expense.currency_id,
                self.budget.currency_id,
            )


        def test_category_actual_breakdown(self):
            self.Expense.create(
                {
                    "name": "Taxi",
                    "budget_id": self.budget.id,
                    "category": "transport",
                    "amount": 1000.0,
                    "is_planned": False,
                }
            )

            self.Expense.create(
                {
                    "name": "Dinner",
                    "budget_id": self.budget.id,
                    "category": "food",
                    "amount": 800.0,
                    "is_planned": False,
                }
            )

            self.Expense.create(
                {
                    "name": "Museum",
                    "budget_id": self.budget.id,
                    "category": "activity",
                    "amount": 700.0,
                    "is_planned": False,
                }
            )

            self.budget.invalidate_recordset()

            self.assertEqual(
                self.budget.actual_transport,
                1000.0,
            )

            self.assertEqual(
                self.budget.actual_food,
                800.0,
            )

            self.assertEqual(
                self.budget.actual_activity,
                700.0,
            )

            self.assertEqual(
                self.budget.actual_spent,
                2500.0,
            )


        def test_planned_expense_is_excluded_from_actual_totals(self):
            self.Expense.create(
                {
                    "name": "Planned Hotel",
                    "budget_id": self.budget.id,
                    "category": "accommodation",
                    "amount": 6000.0,
                    "is_planned": True,
                }
            )

            self.Expense.create(
                {
                    "name": "Paid Hotel",
                    "budget_id": self.budget.id,
                    "category": "accommodation",
                    "amount": 5500.0,
                    "is_planned": False,
                }
            )

            self.budget.invalidate_recordset()

            self.assertEqual(
                self.budget.actual_accommodation,
                5500.0,
            )

            self.assertEqual(
                self.budget.actual_spent,
                5500.0,
            )


        def test_category_overspend_recommendation(self):
            self.Expense.create(
                {
                    "name": "Expensive Food",
                    "budget_id": self.budget.id,
                    "category": "food",
                    "amount": 4500.0,
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

            food_recommendations = recommendations.filtered(
                lambda rec: (
                    rec.recommendation_type == "budget"
                    and "Food spending is high" in rec.name
                )
            )

            self.assertTrue(
                food_recommendations,
            )


        def test_refresh_keeps_accepted_history(self):
            recommendations = (
                self.Recommendation
                .generate_budget_recommendations(
                    self.trip.id
                )
            )

            if not recommendations:
                self.skipTest(
                    "No recommendation generated for this scenario."
                )

            recommendation = recommendations[0]
            recommendation.action_accept()

            self.Recommendation.generate_budget_recommendations(
                self.trip.id
            )

            self.assertTrue(
                recommendation.exists(),
            )

            self.assertEqual(
                recommendation.state,
                "accepted",
            )