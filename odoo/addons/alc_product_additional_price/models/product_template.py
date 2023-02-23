# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.product.models import product_template


class ProductTemplate(product_template.ProductTemplate):

    sale_price_2 = fields.Float(
        digits="Product Price",
        compute="_compute_sale_price_2",
        readonly=True,
        store=False,
        string="Sale Price 2",
    )
    indicated_price = fields.Float(
        string="Indicated price",
        digits="Product Price",
    )

    def _compute_sale_price_2(self):
        pricelist = self.env.ref("alc_product_pricelist_data.product_pricelist_pb2")
        items_sale_price2 = self.env["product.pricelist.item"].search(
            [
                ("pricelist_id", "=", pricelist.id),
                ("applied_on", "=", "1_product"),
                ("product_tmpl_id", "in", self.ids),
            ]
        )
        selected_ids = set(items_sale_price2.product_tmpl_id.ids)
        for product in self:
            product.sale_price_2 = 0
            if product.id not in selected_ids:
                continue
            # We check if product price is modified by the price list
            if product.product_variant_ids:
                price = pricelist._price_get(
                    product=product.product_variant_ids[0], qty=1
                )
                product.sale_price_2 = price.get(pricelist.id, 0.0)
