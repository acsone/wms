# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


# TODO: Check if needed for inventory flows
class StockInventory(models.Model):
    _inherit = "stock.inventory"

    @api.model
    def _default_location_id(self):
        vlb_stock = self.env.ref("stock.stock_location_stock")
        return vlb_stock.location_id.id

    name = fields.Char(default="/")
    location_id = fields.Many2one(default=_default_location_id)
    note = fields.Text("Note")

    INVENTORY_NAMES = ["expensive", "best_sellers", "other"]

    @api.model
    def create(self, vals):
        sequence = self.env["ir.sequence"]

        if vals.get("name") == "/":
            vals["name"] = sequence.next_by_code("stock.inventory")

        return super(StockInventory, self).create(vals)

    @api.multi
    def action_done(self):
        result = super(StockInventory, self).action_done()

        if self.env.context.get("qty_updated"):
            return result

        products = self.line_ids.mapped("product_id")
        products.sudo().write({"date_last_inventory": fields.Datetime.now()})

        return result

    @api.multi
    def _get_empty_product_bin(self, products, quant_products):
        self.ensure_one()
        vals = []
        if products:
            exhausted_products = products - quant_products
            exhausted_domain = [("id", "in", exhausted_products.ids)]
        else:
            exhausted_domain = [("id", "not in", quant_products.ids)]
        exhausted_products = self.env["product.product"].search(exhausted_domain)
        for product in exhausted_products:
            bins = product.stock_bin_ids.mapped("bin_location_id")
            location_id = bins[0].id if bins else self.location_id.id

            vals.append(
                {
                    "inventory_id": self.id,
                    "product_id": product.id,
                    "location_id": location_id,
                }
            )
        return vals


class ProductChangeQuantity(models.TransientModel):
    _inherit = "stock.change.product.qty"

    @api.multi
    def change_product_qty(self):
        """
        When the user update the quantity on hand (with the wizard)
        we don't want to change the last inventory date
        :return:
        """
        return super(
            ProductChangeQuantity, self.with_context(qty_updated=True)
        ).change_product_qty()
