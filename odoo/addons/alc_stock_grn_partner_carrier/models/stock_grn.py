# Copyright (C) 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.stock_grn.models import stock_grn


class StockGrn(stock_grn.StockGrn):

    carrier_category_id = fields.Integer(compute="_compute_carrier_category_id")

    def _compute_carrier_category_id(self):
        carrier_category = self.env.ref(
            "alc_partner_carrier.res_partner_category_carrier"
        )
        for rec in self:
            rec.carrier_category_id = carrier_category.id
