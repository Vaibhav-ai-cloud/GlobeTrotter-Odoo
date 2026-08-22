"""Trip model."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GlobeTrotterTrip(models.Model):
    _name = "globetrotter.trip"
    _description = "GlobeTrotter Trip"
    _order = "start_date desc, id desc"

    name = fields.Char(
        string="Trip Name",
        required=True,
        index=True,
    )

    description = fields.Text(
        string="Description",
    )

    start_date = fields.Date(
        string="Start Date",
        required=True,
        index=True,
    )

    end_date = fields.Date(
        string="End Date",
        required=True,
        index=True,
    )

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Traveler",
        required=True,
        default=lambda self: self.env.user,
        index=True,
        ondelete="restrict",
    )

    stop_ids = fields.One2many(
        comodel_name="globetrotter.trip.stop",
        inverse_name="trip_id",
        string="Trip Stops",
    )

    stop_count = fields.Integer(
        string="Stops",
        compute="_compute_stop_count",
    )

    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("planned", "Planned"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        required=True,
        index=True,
    )

    @api.depends("stop_ids")
    def _compute_stop_count(self):
        for trip in self:
            trip.stop_count = len(trip.stop_ids)

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for trip in self:
            if (
                trip.start_date
                and trip.end_date
                and trip.end_date < trip.start_date
            ):
                raise ValidationError(
                    "Trip end date cannot be earlier than the start date."
                )