from odoo import fields, models


class GlobeTrotterCity(models.Model):
    _name = "globetrotter.city"
    _description = "GlobeTrotter City"
    _order = "name"

    name = fields.Char(
        string="City Name",
        required=True,
        index="trigram",
        help="Official name of the city.",
    )

    country_id = fields.Many2one(
        comodel_name="res.country",
        string="Country",
        required=True,
        ondelete="restrict",
        index=True,
    )

    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="State / Region",
        ondelete="restrict",
        index=True,
    )

    latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
        help="Latitude in decimal degrees.",
    )

    longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
        help="Longitude in decimal degrees.",
    )

    description = fields.Text(
        string="Description",
        help="Short description used for city discovery.",
    )

    image_1920 = fields.Image(
        string="City Image",
        max_width=1920,
        max_height=1920,
    )

    popularity = fields.Integer(
        string="Popularity",
        default=0,
        help="Popularity score used for city discovery and recommendations.",
    )

    cost_index = fields.Float(
        string="Cost Index",
        default=0.0,
        help="Relative city cost index from 0 to 100.",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _unique_city = models.Constraint(
        "UNIQUE(name, country_id)",
        "A city with the same name already exists in this country.",
    )

    _latitude_check = models.Constraint(
        "CHECK(latitude >= -90.0 AND latitude <= 90.0)",
        "Latitude must be between -90 and 90 degrees.",
    )

    _longitude_check = models.Constraint(
        "CHECK(longitude >= -180.0 AND longitude <= 180.0)",
        "Longitude must be between -180 and 180 degrees.",
    )

    _popularity_check = models.Constraint(
        "CHECK(popularity >= 0)",
        "Popularity cannot be negative.",
    )

    _cost_index_check = models.Constraint(
        "CHECK(cost_index >= 0.0 AND cost_index <= 100.0)",
        "Cost Index must be between 0 and 100.",
    )