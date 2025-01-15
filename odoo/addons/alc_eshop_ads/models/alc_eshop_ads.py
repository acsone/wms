# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_lang import Lang
from odoo.addons.fs_file.fields import FSFile


class AlcEshopAds(models.Model):

    _name = "alc.eshop.ads"
    # nosemgrep: is-old-style-inheritance
    _inherit = [
        "alc.eshop.temporal.info.mixin",
        "fs.image.mixin",
        "mixin.past",
    ]
    _description = "Eshop Ads"

    name = fields.Char(required=True)
    visibility = fields.Selection(
        required=True,
        selection=[
            ("everyone", "Everyone"),
            ("shareholder", "Shareholder"),
            ("non-shareholder", "Non Shareholder"),
            ("shareholder-under-contract", "Shareholder under contract"),
        ],
        default="everyone",
    )
    file = FSFile(
        help="If specified, the file will be downloaded by the customer upon "
        "click on the ads banner into the website.",
    )

    site_url = fields.Char(
        string="Site url",
        help="If specified, the customer will be redirected to this url upon click "
        "on the ads banner into the website.",
    )
    display_slot = fields.Selection(
        selection=[
            ("top_left", "Top left"),
            ("top_right", "Top right"),
            ("bottom_left", "Bottom left"),
            ("bottom_right", "Bottom right"),
        ],
        required=True,
    )
    lang_id = fields.Many2one[Lang](
        string="Lang",
        help="If set, the ads will be only visible into the specified "
        "lang on the website",
    )
    display_time = fields.Integer(required=True, default=-1)

    @api.constrains("site_url", "file")
    def _check_site_url_or_file(self):
        for rec in self:
            if rec.site_url and rec.file:
                raise ValidationError(
                    _(
                        "You must choose between the download of a file OR the "
                        "redirect to a website on click on the banner"
                    )
                )

    def get_display_slot_label(self):
        return self._fields.get("display_slot").convert_to_export(
            self.display_slot, self
        )

    @api.depends("name", "date_start", "date_end", "display_slot")
    def _compute_display_name(self):
        qweb_date = self.env["ir.qweb.field.date"]
        for rec in self:
            rec.display_name = (
                f"{rec.name} - {rec.get_display_slot_label()} "
                f"({qweb_date.value_to_html(rec.date_start, {})} -> "
                f"{qweb_date.value_to_html(rec.date_end, {})})"
            )
