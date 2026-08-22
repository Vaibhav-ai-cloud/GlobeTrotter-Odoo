from odoo import api, fields, models


class GlobeTrotterProfile(models.Model):
    _name = "globetrotter.profile"
    _description = "GlobeTrotter User Profile"
    _rec_name = "profile_name"
    _order = "profile_name, id"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="User",
        required=True,
        default=lambda self: self.env.user,
        ondelete="cascade",
        index=True,
    )

    profile_name = fields.Char(
        string="Profile Name",
        required=True,
        default=lambda self: self.env.user.name,
    )

    image_1920 = fields.Image(
        string="Profile Image",
        max_width=1920,
        max_height=1920,
    )

    bio = fields.Text(string="Bio")

    _user_unique = models.Constraint(
        "UNIQUE(user_id)",
        "Each user can have only one GlobeTrotter profile.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.setdefault("user_id", self.env.user.id)
            vals.setdefault("profile_name", self.env.user.name)
        return super().create(vals_list)
