from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GlobeTrotterExpense(models.Model):

    _name = "globetrotter.expense"
    _description = "Trip Expense"
    _order = "expense_date desc, id desc"

    name = fields.Char(
        string="Expense",
        required=True,
    )

    trip_id = fields.Many2one(
        "globetrotter.trip",
        string="Trip",
        required=True,
        ondelete="cascade",
    )

    budget_id = fields.Many2one(
        "globetrotter.budget",
        string="Budget",
        ondelete="cascade",
    )

    category = fields.Selection(
        [
            ("transport", "Transport"),
            ("accommodation", "Stay"),
            ("food", "Food"),
            ("activity", "Activity"),
            ("other", "Other"),
        ],
        string="Category",
        required=True,
        default="other",
    )

    amount = fields.Monetary(
        string="Amount",
        required=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    expense_date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )

    description = fields.Text(
        string="Description",
    )

    is_planned = fields.Boolean(
        string="Planned Expense",
        default=True,
    )

    @api.onchange("budget_id")
    def _onchange_budget_id(self):
        if self.budget_id:
            self.trip_id = self.budget_id.trip_id
            self.currency_id = self.budget_id.currency_id

    @api.constrains("amount")
    def _check_amount(self):
        for record in self:
            if record.amount <= 0:
                raise ValidationError(
                    "Expense amount must be greater than zero."
                )

    @api.constrains("budget_id", "trip_id")
    def _check_budget_trip(self):
        for record in self:
            if (
                record.budget_id
                and record.trip_id
                and record.budget_id.trip_id != record.trip_id
            ):
                raise ValidationError(
                    "The selected budget must belong to the same trip."
                )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            budget_id = vals.get("budget_id")

            if budget_id:
                budget = self.env["globetrotter.budget"].browse(budget_id)

                if budget.exists():
                    vals.setdefault("trip_id", budget.trip_id.id)
                    vals.setdefault("currency_id", budget.currency_id.id)

        return super().create(vals_list)


    def write(self, vals):
        result = super().write(vals)

        for record in self:
            if record.budget_id:
                update_vals = {}

                if record.trip_id != record.budget_id.trip_id:
                    update_vals["trip_id"] = record.budget_id.trip_id.id

                if record.currency_id != record.budget_id.currency_id:
                    update_vals["currency_id"] = record.budget_id.currency_id.id

                if update_vals:
                    super(GlobeTrotterExpense, record).write(update_vals)

        return result
