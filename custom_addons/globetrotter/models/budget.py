from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GlobeTrotterBudget(models.Model):
    _name = "globetrotter.budget"
    _description = "Trip Budget"
    _order = "id desc"

    name = fields.Char(
        string="Budget Name",
        required=True,
        default="Trip Budget",
    )

    trip_id = fields.Many2one(
        "globetrotter.trip",
        string="Trip",
        required=True,
        ondelete="cascade",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    total_budget = fields.Monetary(
        string="Total Budget",
        currency_field="currency_id",
        required=True,
        default=0.0,
    )

    transport_budget = fields.Monetary(
        string="Transport",
        currency_field="currency_id",
        default=0.0,
    )

    accommodation_budget = fields.Monetary(
        string="Stay",
        currency_field="currency_id",
        default=0.0,
    )

    food_budget = fields.Monetary(
        string="Food",
        currency_field="currency_id",
        default=0.0,
    )

    activity_budget = fields.Monetary(
        string="Activities",
        currency_field="currency_id",
        default=0.0,
    )

    other_budget = fields.Monetary(
        string="Other",
        currency_field="currency_id",
        default=0.0,
    )

    planned_total = fields.Monetary(
        string="Planned Cost",
        currency_field="currency_id",
        compute="_compute_budget_summary",
        store=True,
    )

    remaining_budget = fields.Monetary(
        string="Remaining Budget",
        currency_field="currency_id",
        compute="_compute_budget_summary",
        store=True,
    )

    budget_usage = fields.Float(
        string="Budget Used (%)",
        compute="_compute_budget_summary",
        store=True,
    )

    is_over_budget = fields.Boolean(
        string="Over Budget",
        compute="_compute_budget_summary",
        store=True,
    )
    
    expense_ids = fields.One2many(
        "globetrotter.expense",
        "budget_id",
        string="Expenses",
    )
    
    actual_spent = fields.Monetary(
        string="Actual Spent",
        currency_field="currency_id",
        compute="_compute_actual_expenses",
        store=True,
    )

    actual_remaining = fields.Monetary(
        string="Actual Remaining",
        currency_field="currency_id",
        compute="_compute_actual_expenses",
        store=True,
    )

    actual_usage = fields.Float(
        string="Actual Budget Used (%)",
        compute="_compute_actual_expenses",
        store=True,
    )

    is_actual_over_budget = fields.Boolean(
        string="Actually Over Budget",
        compute="_compute_actual_expenses",
        store=True,
    )
    actual_transport = fields.Monetary(
        string="Actual Transport",
        currency_field="currency_id",
        compute="_compute_actual_expenses",
        store=True,
    )

    actual_accommodation = fields.Monetary(
        string="Actual Stay",
        currency_field="currency_id",
        compute="_compute_actual_expenses",
        store=True,
    )

    actual_food = fields.Monetary(
        string="Actual Food",
        currency_field="currency_id",
        compute="_compute_actual_expenses",
        store=True,
    )

    actual_activity = fields.Monetary(
        string="Actual Activities",
        currency_field="currency_id",
        compute="_compute_actual_expenses",
        store=True,
    )

    actual_other = fields.Monetary(
        string="Actual Other",
        currency_field="currency_id",
        compute="_compute_actual_expenses",
        store=True,
    )
    
    @api.depends(
    "expense_ids.amount",
    "expense_ids.category",
    "total_budget",
)
def _compute_actual_expenses(self):
    for record in self:
        transport = 0.0
        accommodation = 0.0
        food = 0.0
        activity = 0.0
        other = 0.0

        for expense in record.expense_ids:
            if expense.category == "transport":
                transport += expense.amount
            elif expense.category == "accommodation":
                accommodation += expense.amount
            elif expense.category == "food":
                food += expense.amount
            elif expense.category == "activity":
                activity += expense.amount
            else:
                other += expense.amount

        record.actual_transport = transport
        record.actual_accommodation = accommodation
        record.actual_food = food
        record.actual_activity = activity
        record.actual_other = other

        record.actual_spent = (
            transport
            + accommodation
            + food
            + activity
            + other
        )

        record.actual_remaining = (
            record.total_budget - record.actual_spent
        )

        record.is_actual_over_budget = (
            record.actual_spent > record.total_budget
        )

        if record.total_budget > 0:
            record.actual_usage = (
                record.actual_spent / record.total_budget
            ) * 100
        else:
            record.actual_usage = 0.0

    @api.depends(
        "total_budget",
        "transport_budget",
        "accommodation_budget",
        "food_budget",
        "activity_budget",
        "other_budget",
    )
    def _compute_budget_summary(self):
        for record in self:
            record.planned_total = (
                record.transport_budget
                + record.accommodation_budget
                + record.food_budget
                + record.activity_budget
                + record.other_budget
            )

            record.remaining_budget = (
                record.total_budget - record.planned_total
            )

            record.is_over_budget = (
                record.planned_total > record.total_budget
            )

            if record.total_budget > 0:
                record.budget_usage = (
                    record.planned_total / record.total_budget
                ) * 100
            else:
                record.budget_usage = 0.0

    @api.constrains(
        "total_budget",
        "transport_budget",
        "accommodation_budget",
        "food_budget",
        "activity_budget",
        "other_budget",
    )
    def _check_negative_amounts(self):
        for record in self:
            amounts = [
                record.total_budget,
                record.transport_budget,
                record.accommodation_budget,
                record.food_budget,
                record.activity_budget,
                record.other_budget,
            ]

            if any(amount < 0 for amount in amounts):
                raise ValidationError(
                    "Budget amounts cannot be negative."
                )