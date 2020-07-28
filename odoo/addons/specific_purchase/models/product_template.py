# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    volume = fields.Float(
        string="Volume (liter)", help="Volume in liter", digits=(12, 3)
    )

    length = fields.Float("Length (cm)", help="Length in cm")
    width = fields.Float("Width (cm)", help="Width in cm")
    depth = fields.Float("Depth (cm)", help="Depth in cm")
    supplier_id = fields.Many2one(
        "res.partner",
        string="Vendor",
        readonly=True,
        domain=[("supplier", "=", True)],
        related="seller_ids.name",
        store=True,
        index=True,
    )
    vendor_product_code = fields.Char(
        "Vendor Product Code",
        readonly=True,
        related="seller_ids.product_code",
        store=True,
        index=True,
    )
    state_id = fields.Many2one("product.state", string="State")
    nb_days_out_of_stock = fields.Integer(
        help="Number of days before running out of stock",
        compute="compute_date_out_of_stock",
    )

    @api.onchange("length", "width", "depth")
    def onchange_size(self):
        """
        Alcyon use centimeter for the length but use the liter for the volume.
        As a reminder: 1 cm³ = 0.001 liter and 1000 cm³ = 1 liter
        :return:
        """
        for product in self:
            volume_in_cm3 = product.length * product.width * product.depth
            volume_in_liter = volume_in_cm3 / 1000
            product.volume = volume_in_liter

    @api.onchange("route_ids")
    def compute_date_out_of_stock(self):
        route_mto = self.env.ref("stock.route_warehouse0_mto")
        route_mto_mts = self.env.ref("stock_mts_mto_rule.route_mto_mts")
        route_ids = [route_mto.id, route_mto_mts.id]
        for product in self:
            if (
                any(route in product.route_ids.ids for route in route_ids)
                or product.product_variant_count > 1
            ):
                product.nb_days_out_of_stock = 0
            else:
                avg_csp = product.product_variant_id.average_annual_consumption
                daily_csp = (12 * avg_csp) / 365.0
                nb_days_out_of_stock = product.virtual_available * daily_csp
                product.nb_days_out_of_stock = nb_days_out_of_stock


class ProductState(models.Model):
    _name = "product.state"
    _order = "sequence"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True)
    sequence = fields.Integer()


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

        if not limit:
            limit = 100

        result = super(ProductProduct, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )

        if len(result) >= limit:
            return result

        limit_available = limit - len(result)
        existing_ids = [x[0] for x in result]
        products = self.search(
            [("vendor_product_code", "=", name), ("id", "not in", existing_ids)] + args,
            limit=limit_available,
        )

        result += products.name_get()
        return result
