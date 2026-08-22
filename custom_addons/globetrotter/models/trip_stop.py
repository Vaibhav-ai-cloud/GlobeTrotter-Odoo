"""Trip stop model."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GlobeTrotterTripStop(models.Model):
    _name = "globetrotter.trip.stop"
    _description = "GlobeTrotter Trip Stop"
    _order = "trip_id, sequence, id"

    trip_id = fields.Many2one(
        comodel_name="globetrotter.trip",
        string="Trip",
        required=True,
        index=True,
        ondelete="cascade",
    )

    city_id = fields.Many2one(
        comodel_name="globetrotter.city",
        string="City",
        required=True,
        index=True,
        ondelete="restrict",
    )

    sequence = fields.Integer(
        string="Sequence",
        required=True,
        default=10,
        index=True,
    )

    arrival_date = fields.Date(
        string="Arrival Date",
        required=True,
    )

    departure_date = fields.Date(
        string="Departure Date",
        required=True,
    )

    duration = fields.Integer(
        string="Duration (Days)",
        compute="_compute_duration",
        store=True,
    )

    notes = fields.Text(
        string="Notes",
    )

    @api.depends("arrival_date", "departure_date")
    def _compute_duration(self):
        for stop in self:
            if stop.arrival_date and stop.departure_date:
                stop.duration = (
                    stop.departure_date - stop.arrival_date
                ).days + 1
            else:
                stop.duration = 0

    @api.constrains("arrival_date", "departure_date")
    def _check_dates(self):
        for stop in self:
            if (
                stop.arrival_date
                and stop.departure_date
                and stop.departure_date < stop.arrival_date
            ):
                raise ValidationError(
                    "Departure date cannot be earlier than arrival date."
                )

    @api.constrains("sequence")
    def _check_sequence(self):
        for stop in self:
            if stop.sequence < 1:
                raise ValidationError(
                    "Stop sequence must be greater than or equal to 1."
                )