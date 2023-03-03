# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

import odoo.addons.decimal_precision as dp


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _order = "default_code"

    medical_device = fields.Boolean(string="Medical Device")

    sale_price_2 = fields.Float(
        digits=dp.get_precision("Product Price"),
        compute="_compute_sale_price_2",
        readonly=True,
        store=False,
        string="Sale Price 2",
    )  # TODO: has been moved to alc_product_additional_price

    indicated_price = fields.Float(
        string="Indicated price", digits=dp.get_precision("Product Price")
    )  # TODO: has been moved to alc_product_additional_price

    storage_temperature_id = fields.Many2one(
        "product.storage.temperature", string="Storage temperature"
    )

    web_published = fields.Boolean(string="Published on website")

    count_pickings_to_do = fields.Integer(
        string="Incoming Pickings", compute="_compute_incoming_pickings"
    )

    def _compute_sale_price_2(self):
        for product in self:
            pricelist = self.env.ref("alc_product_pricelist_data.product_pricelist_pb2")

            item_count = self.env["product.pricelist.item"].search_count(
                [
                    ("pricelist_id", "=", pricelist.id),
                    ("applied_on", "=", "1_product"),
                    ("product_tmpl_id", "=", product.id),
                ]
            )

            # We check if product price is modified by the price list
            if item_count and product.product_variant_ids:
                price = pricelist.price_get(
                    prod_id=product.product_variant_ids[0].id, qty=1
                )
                product.sale_price_2 = price.get(pricelist.id, 0.0)

    def action_open_incoming_stock_moves(self):
        action = super(ProductTemplate, self).action_view_stock_moves()
        action["context"]["search_default_future"] = 1
        action["context"]["search_default_groupby_picking_id"] = 1
        action["domain"].append(("picking_type_id.code", "=", "incoming"))
        return action

    def _compute_incoming_pickings(self):
        for rec in self:
            rec.count_pickings_to_do = sum(
                rec.mapped("product_variant_ids.count_pickings_to_do")
            )
