# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AlcEshopInfoBanner(models.Model):

    _name = "alc.eshop.info.banner"
    _inherit = "alc.eshop.temporal.info.mixin"  # nosemgrep: is-old-style-inheritance
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

    def _compute_display_name(self):
        for record in self:
            record.display_name = record.html[:50]
