# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.alc_product_average_sale.models.product_product import (
    ProductProduct as ProductProductBase,
)


class ProductProduct(ProductProductBase):

    nb_days_out_of_stock = fields.Integer(
        help="Number of days before running out of stock",
        compute="_compute_date_out_of_stock",
    )

    @api.depends("route_ids", "average_annual_sale", "virtual_available")
    def _compute_date_out_of_stock(self):
        warehouses = self.env["stock.warehouse"].search(
            [("company_id", "=", self.env.company.id)]
        )
        mto_routes = warehouses.mto_pull_id.route_id
        for product in self:
            if set(mto_routes).intersection(set(product.route_ids)):
                product.nb_days_out_of_stock = 0
            else:
                avg_csp = product.average_annual_sale
                daily_csp = (12 * avg_csp) / 365.0
                nb_days_out_of_stock = product.virtual_available * daily_csp
                product.nb_days_out_of_stock = nb_days_out_of_stock
