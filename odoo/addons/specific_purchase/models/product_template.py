# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    nb_days_out_of_stock = fields.Integer(
        help="Number of days before running out of stock",
        compute="_compute_date_out_of_stock",
    )

    @api.onchange("route_ids")
    def _compute_date_out_of_stock(self):
        route_mto = self.env.ref("stock.route_warehouse0_mto")
        for product in self:
            if route_mto in product.route_ids.ids or product.product_variant_count > 1:
                product.nb_days_out_of_stock = 0
            else:
                avg_csp = product.product_variant_id.average_annual_consumption
                daily_csp = (12 * avg_csp) / 365.0
                nb_days_out_of_stock = product.virtual_available * daily_csp
                product.nb_days_out_of_stock = nb_days_out_of_stock
