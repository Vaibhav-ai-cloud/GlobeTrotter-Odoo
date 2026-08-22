from odoo import fields, models


class GlobeTrotterItinerary(models.Model):
    _name = "globetrotter.itinerary"
    _description = "GlobeTrotter Itinerary"
    _order = "sequence, start_datetime, id"

    name = fields.Char(
        string="Title",
        required=True,
        index="trigram",
    )

    activity_id = fields.Many2one(
        comodel_name="globetrotter.activity",
        string="Activity",
        ondelete="restrict",
        index=True,
    )

    start_datetime = fields.Datetime(
        string="Start Date & Time",
        required=True,
        index=True,
    )

    end_datetime = fields.Datetime(
        string="End Date & Time",
        required=True,
        index=True,
    )

    notes = fields.Text(
        string="Notes",
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        index=True,
    )

    status = fields.Selection(
        selection=[
            ("planned", "Planned"),
            ("confirmed", "Confirmed"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        required=True,
        default="planned",
        index=True,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _datetime_check = models.Constraint(
        "CHECK(end_datetime > start_datetime)",
        "End Date & Time must be later than Start Date & Time.",
    )