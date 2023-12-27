# © 2017 Sylvain Van Hoof (Okia SPRL)
# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from unidecode import unidecode

from odoo import api, fields

from odoo.addons.base.models.res_partner import Partner


class ResPartner(Partner):

    is_price_on_labels = fields.Boolean("Display price on labels")
    normalized_name = fields.Char(compute="_compute_normalized_name")
    normalized_display_name = fields.Char(compute="_compute_normalized_name")

    @api.depends("name")
    def _compute_normalized_name(self):
        for rec in self:
            rec.normalized_name = unidecode(rec.name)
            rec.normalized_display_name = unidecode(rec.display_name)
