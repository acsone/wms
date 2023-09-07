# Copyright 2023 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields

from odoo.addons.account_intrastat.models.product import ProductProduct as Product


class ProductProduct(Product):

    has_intrastat = fields.Boolean(compute="_compute_has_intrastat", store=False)
    intrastat_code_name = fields.Char(related="intrastat_code_id.name", store=False)

    @api.depends("intrastat_code_id", "intrastat_code_id.name")
    def _compute_has_intrastat(self):
        for rec in self:
            rec.has_intrastat = rec.intrastat_code_id
