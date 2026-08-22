from odoo import api, fields, models


class GlobeTrotterRecommendation(models.Model):
    _name = "globetrotter.recommendation"
    _description = "Trip Recommendation"
    _order = "score desc, id desc"

    name = fields.Char(
        string="Recommendation",
        required=True,
    )

    trip_id = fields.Many2one(
        "globetrotter.trip",
        string="Trip",
        required=True,
        ondelete="cascade",
        index=True,
    )

    budget_id = fields.Many2one(
        "globetrotter.budget",
        string="Budget",
        ondelete="cascade",
        index=True,
    )

    recommendation_type = fields.Selection(
        [
            ("budget", "Budget Optimization"),
            ("activity", "Activity Suggestion"),
            ("schedule", "Schedule Improvement"),
            ("general", "General"),
        ],
        string="Type",
        required=True,
        default="general",
    )

    message = fields.Text(
        string="Recommendation Message",
        required=True,
    )

    estimated_saving = fields.Monetary(
        string="Estimated Saving",
        currency_field="currency_id",
        default=0.0,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    score = fields.Float(
        string="Priority Score",
        default=0.0,
        help="Higher score means a higher recommendation priority.",
    )

    state = fields.Selection(
        [
            ("new", "New"),
            ("accepted", "Accepted"),
            ("dismissed", "Dismissed"),
        ],
        string="Status",
        default="new",
        required=True,
    )

    active = fields.Boolean(
        default=True,
    )

    def action_accept(self):
        self.write({"state": "accepted"})
        return True

    def action_dismiss(self):
        self.write({"state": "dismissed"})
        return True

    @api.model
    def generate_budget_recommendations(self, trip_id):
        """Generate budget recommendations for one trip."""
        if not trip_id:
            return self.browse()

        Budget = self.env["globetrotter.budget"]

        budget = Budget.search(
            [("trip_id", "=", trip_id)],
            order="id desc",
            limit=1,
        )

        if not budget:
            return self.browse()

        # Remove only previous active/new budget suggestions generated
        # for this budget. Accepted/dismissed history stays untouched.
        old_recommendations = self.search(
            [
                ("trip_id", "=", trip_id),
                ("budget_id", "=", budget.id),
                ("recommendation_type", "=", "budget"),
                ("state", "=", "new"),
            ]
        )
        old_recommendations.unlink()

        recommendations = self.browse()

        if budget.total_budget <= 0:
            recommendations |= self.create(
                {
                    "name": "Set a trip budget",
                    "trip_id": trip_id,
                    "budget_id": budget.id,
                    "recommendation_type": "budget",
                    "message": (
                        "Set a total trip budget to enable cost tracking "
                        "and personalized budget recommendations."
                    ),
                    "currency_id": budget.currency_id.id,
                    "score": 100.0,
                }
            )
            return recommendations

        # Actual spending has crossed the total budget.
        if budget.actual_spent > budget.total_budget:
            exceeded_by = budget.actual_spent - budget.total_budget

            recommendations |= self.create(
                {
                    "name": "Trip is over budget",
                    "trip_id": trip_id,
                    "budget_id": budget.id,
                    "recommendation_type": "budget",
                    "message": (
                        f"Your actual trip spending exceeds the total "
                        f"budget by {exceeded_by:.2f}. Review high-cost "
                        f"categories before adding more expenses."
                    ),
                    "estimated_saving": exceeded_by,
                    "currency_id": budget.currency_id.id,
                    "score": 100.0,
                }
            )

        # Budget usage is getting high.
        elif budget.actual_usage >= 80:
            recommendations |= self.create(
                {
                    "name": "Budget usage is high",
                    "trip_id": trip_id,
                    "budget_id": budget.id,
                    "recommendation_type": "budget",
                    "message": (
                        f"You have already used "
                        f"{budget.actual_usage:.1f}% of your trip budget. "
                        f"Consider lower-cost options for upcoming expenses."
                    ),
                    "currency_id": budget.currency_id.id,
                    "score": 85.0,
                }
            )

        # Planned expenses exceed available budget.
        if budget.planned_total > budget.total_budget:
            planned_excess = budget.planned_total - budget.total_budget

            recommendations |= self.create(
                {
                    "name": "Planned cost exceeds budget",
                    "trip_id": trip_id,
                    "budget_id": budget.id,
                    "recommendation_type": "budget",
                    "message": (
                        f"Your planned trip cost is "
                        f"{planned_excess:.2f} above the available budget. "
                        f"Reduce one or more planned expense categories."
                    ),
                    "estimated_saving": planned_excess,
                    "currency_id": budget.currency_id.id,
                    "score": 90.0,
                }
            )

        # Identify the largest planned cost category.
        category_amounts = {
            "transport": budget.transport_budget,
            "stay": budget.accommodation_budget,
            "food": budget.food_budget,
            "activities": budget.activity_budget,
            "other": budget.other_budget,
        }

        largest_category = max(
            category_amounts,
            key=category_amounts.get,
        )
        largest_amount = category_amounts[largest_category]

        if (
            budget.total_budget > 0
            and largest_amount > budget.total_budget * 0.40
        ):
            possible_saving = largest_amount * 0.10

            recommendations |= self.create(
                {
                    "name": f"Optimize {largest_category} cost",
                    "trip_id": trip_id,
                    "budget_id": budget.id,
                    "recommendation_type": "budget",
                    "message": (
                        f"{largest_category.title()} represents a large "
                        f"share of your planned budget. Comparing lower-cost "
                        f"alternatives could reduce your overall trip cost."
                    ),
                    "estimated_saving": possible_saving,
                    "currency_id": budget.currency_id.id,
                    "score": 70.0,
                }
            )

        return recommendations