# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    supplier_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        readonly=True,
        domain=[("supplier", "=", True)],
        related="seller_ids.name",
        store=True,
        index=True,
    )
    # TODO: move supplier fields to new module alc_product_supplier
    supplier_rel_id = fields.Integer(
        string="Vendor ID", readonly=True, related="supplier_id.id", store=False,
    )
    vendor_product_code = fields.Char(
        "Vendor Product Code",
        readonly=True,
        related="seller_ids.product_code",
        store=True,
        index=True,
    )
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


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """
        When want to be able to search by the vendor product product.
        However we cannot simply modify args by adding the domain
        [('vendor_product_code', '=', name)].

        The solution is to execute the method and look if the number of records
        found is less than the limit. It means that Odoo don't found
        all records. In this case, I search with the vendor_product_code.
        """
        if not args:
            args = []

        result = super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )

        if limit and len(result) >= limit:
            return result

        limit_available = None
        if limit:
            limit_available = limit - len(result)
        existing_ids = [x[0] for x in result]
        products = self.search(
            [("vendor_product_code", "=", name), ("id", "not in", existing_ids)] + args,
            limit=limit_available,
        )

        result += products.name_get()
        return result
