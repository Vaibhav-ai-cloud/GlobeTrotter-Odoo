"""City model."""

from odoo import fields, models


class GlobeTrotterCity(models.Model):
    _name = "globetrotter.city"
    _description = "Travel City"
    _order = "name"

    name = fields.Char(
        string="City Name",
        required=True,
        index=True,
    )

    country = fields.Char(
        string="Country",
        required=True,
    )

    description = fields.Text(
        string="Description",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )