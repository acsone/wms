# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class AlcProductPartnerPrice(models.Model):

    _name = "alc.product.partner.price"
    _description = "Alc Product Partner Price"

    product_id = fields.Many2one(
        comodel_name="product.product", index=True, required=True
    )
    partner_id = fields.Many2one(comodel_name="res.partner", required=True)
    supplier_discount = fields.Float(digits=dp.get_precision("Discount"), default=0.0,)
    alcyon_discount = fields.Float(digits=dp.get_precision("Discount"), default=0.0,)
    unit_price = fields.Float(
        string="Unit price",
        digits=dp.get_precision("Product Price"),
        help="Price computed from list_price and property_product_pricelist",
    )
    net_price = fields.Float(
        string="Net price",
        digits=dp.get_precision("Product Price"),
        help="unit_price with promotions applied",
    )

    @api.model
    def _get_supplier_discount(self, product):
        seller = product._select_seller_for_sale(
            partner_id=False,
            quantity=1.0,
            date=fields.Date.today(),
            uom_id=product.uom_id,
        )
        return seller.discount_sale or 0.0

    @api.model
    def _get_alcyon_discount(self, product, partner):
        price_rule = partner.discount_pricelist_id.get_product_price_rule(
            product, 1.0, partner
        )
        alcyon_discount = 0.0
        if price_rule and len(price_rule) == 2 and price_rule[1]:
            rule = self.env["product.pricelist.item"].browse(price_rule[1])

            if rule.compute_price == "percentage":
                alcyon_discount = rule.percent_price
            else:
                price_unit = product.price
                alcyon_discount = (price_unit - price_rule[0]) / price_unit * 100
        return alcyon_discount

    def _get_final_discount(self, *discounts):
        discounts = [1 - (discount or 0.0) / 100 for discount in discounts]
        final_discount = 1
        for discount in discounts:
            final_discount *= discount
        return 100 - final_discount * 100

    @api.model
    def _compute_for_partner(self, partner, product_domain=None):
        product_domain = product_domain or []
        self.env.cr.execute(
            """delete from %(table)s where partner_id = %(partner_id)s""",
            {"table": AsIs(self._table), "partner_id": partner.id},
        )
        products = self.env["product.product"].search(product_domain)
        products = products.with_context(
            partner_id=partner.id,
            pricelist=partner.property_product_pricelist.id,
            quantity=1.0,
        )
        for product in products:
            supplier_discount = self._get_supplier_discount(product)
            alcyon_discount = self._get_alcyon_discount(product, partner)
            final_discount = self._get_final_discount(
                supplier_discount, alcyon_discount
            )
            price = product.price * (1.0 - final_discount / 100.0)
            vals = {
                "product_id": product.id,
                "partner_id": partner.id,
                "unit_price": product.price,
                "supplier_discount": supplier_discount,
                "alcyon_discount": alcyon_discount,
                "net_price": price,
            }
            self.create(vals)
