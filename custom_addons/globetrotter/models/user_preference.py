from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GlobeTrotterUserPreference(models.Model):
    _name = "globetrotter.user.preference"
    _description = "GlobeTrotter User Travel Preference"
    _rec_name = "user_id"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.user,
        index=True,
    )

    travel_style = fields.Selection(
        [
            ("budget", "Budget"),
            ("balanced", "Balanced"),
            ("premium", "Premium"),
        ],
        string="Travel Style",
        required=True,
        default="balanced",
    )

    preferred_activity_type = fields.Selection(
        [
            ("adventure", "Adventure"),
            ("culture", "Culture"),
            ("nature", "Nature"),
            ("food", "Food"),
            ("shopping", "Shopping"),
            ("relaxation", "Relaxation"),
            ("mixed", "Mixed"),
        ],
        string="Preferred Activity Type",
        default="mixed",
        required=True,
    )

    daily_budget = fields.Monetary(
        string="Preferred Daily Budget",
        currency_field="currency_id",
        default=0.0,
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    prefers_low_cost = fields.Boolean(
        string="Prefer Cost-Saving Options",
        default=False,
    )

    notes = fields.Text(
        string="Travel Preference Notes",
    )

    active = fields.Boolean(
        default=True,
    )

    _user_unique = models.Constraint(
        "UNIQUE(user_id)",
        "Each user can have only one travel preference profile.",
    )

    @api.constrains("daily_budget")
    def _check_daily_budget(self):
        for record in self:
            if record.daily_budget < 0:
                raise ValidationError(
                    "Preferred daily budget cannot be negative."
                )