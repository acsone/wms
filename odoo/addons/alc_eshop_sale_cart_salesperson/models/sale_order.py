# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api

from odoo.addons.shopinvader_sale_cart.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    @api.model
    def _prepare_cart(self, partner_id):
        vals = super()._prepare_cart(partner_id)
        vals["user_id"] = self.env.ref(
            "alc_eshop_sale_cart_salesperson.eshop_salesperson"
        ).id
        return vals
