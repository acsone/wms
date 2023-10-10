# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AlcEshopInfoBanner(models.Model):

    _name = "alc.eshop.info.banner"
    _description = "Eshop Info Banner"

    html = fields.Html(required=True, translate=True)
    type = fields.Selection(
        selection=[("info", "info"), ("warning", "warning")],
        required=True,
        default="info",
    )
    visibility = fields.Selection(
        selection=[
            ("all", "ALL"),
            ("auth_only", "Authenticated Only"),
            ("public_only", "Public Only"),
        ],
        required=True,
        default="auth_only",
    )
    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True)

    @api.constrains("date_start", "date_end")
    def _validate_dates(self):
        for this in self:
            if this.date_start > this.date_end:
                raise ValidationError(
                    _(
                        "The defined period is not valid (%(start)s > %(end)s)",
                        start=this.date_start,
                        end=this.date_end,
                    )
                )
