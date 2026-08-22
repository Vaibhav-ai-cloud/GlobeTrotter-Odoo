from odoo import fields, models


class GlobeTrotterActivity(models.Model):
    _name = "globetrotter.activity"
    _description = "GlobeTrotter Activity"
    _order = "city_id, sequence, name"

    name = fields.Char(
        string="Activity Name",
        required=True,
        index="trigram",
    )

    city_id = fields.Many2one(
        comodel_name="globetrotter.city",
        string="City",
        required=True,
        ondelete="restrict",
        index=True,
    )

    category = fields.Selection(
        selection=[
            ("sightseeing", "Sightseeing"),
            ("adventure", "Adventure"),
            ("culture", "Culture"),
            ("food", "Food & Drink"),
            ("nature", "Nature"),
            ("shopping", "Shopping"),
            ("entertainment", "Entertainment"),
            ("wellness", "Wellness"),
            ("other", "Other"),
        ],
        string="Category",
        required=True,
        default="sightseeing",
        index=True,
    )

    description = fields.Text(
        string="Description",
    )

    duration = fields.Float(
        string="Duration (Hours)",
        required=True,
        default=1.0,
        help="Expected activity duration in hours.",
    )

    estimated_cost = fields.Monetary(
        string="Estimated Cost",
        currency_field="currency_id",
        help="Estimated cost per person.",
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
        ondelete="restrict",
    )

    latitude = fields.Float(
        string="Latitude",
        digits=(10, 7),
    )

    longitude = fields.Float(
        string="Longitude",
        digits=(10, 7),
    )

    image_1920 = fields.Image(
        string="Activity Image",
        max_width=1920,
        max_height=1920,
    )

    sequence = fields.Integer(
        string="Sequence",
        default=10,
        index=True,
    )

    popularity = fields.Integer(
        string="Popularity",
        default=0,
        help="Popularity score used for activity discovery.",
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    _duration_check = models.Constraint(
        "CHECK(duration > 0)",
        "Activity duration must be greater than zero.",
    )

    _estimated_cost_check = models.Constraint(
        "CHECK(estimated_cost >= 0)",
        "Estimated cost cannot be negative.",
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

    _unique_activity = models.Constraint(
        "UNIQUE(name, city_id)",
        "An activity with the same name already exists in this city.",
    )