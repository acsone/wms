# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    supplier_promotion_allowed = fields.Boolean(
        string="Supplier promotion allowed",
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    discount_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Alcyon Discount",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    @api.model
    def create(self, vals):
        """ Fills discount pricelist field (if it is not)
        based on partner configuration.
        """
        partner_id = vals.get("partner_id")
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id)
            if "discount_pricelist_id" not in vals:
                pricelist = partner["discount_pricelist_id"]
                if pricelist:
                    vals["discount_pricelist_id"] = pricelist.id
            if "supplier_promotion_allowed" not in vals:
                vals[
                    "supplier_promotion_allowed"
                ] = partner.supplier_promotion_sale_allowed

        return super(SaleOrder, self).create(vals)

    @api.onchange("partner_id")
    def onchange_partner_id_discount_pricelist(self):
        """ Update promotion and discount pricelist fields
        when partner_id is updated.
        """
        self.supplier_promotion_allowed = (
            self.partner_id.supplier_promotion_sale_allowed
        )
        self.discount_pricelist_id = self.partner_id.discount_pricelist_id

    @api.onchange("supplier_promotion_allowed")
    def onchange_supplier_promotion_allowed(self):
        self.order_line.compute_supplier_promotion()

    @api.onchange("discount_pricelist_id")
    def onchange_discount_pricelist_id(self):
        self.order_line.compute_alcyon_discount()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def compute_supplier_promotion(self):
        for line in self:
            discount2 = False

            condition = line.product_id and line.order_id.supplier_promotion_allowed
            if condition:

                seller = line.product_id._select_seller_for_sale(
                    partner_id=False,
                    quantity=line.product_uom_qty,
                    date=(line.order_id.date_order and line.order_id.date_order[:10]),
                    uom_id=line.product_uom,
                )

                if seller:
                    discount2 = seller.discount_sale
            line.discount2 = discount2

    @api.multi
    def compute_alcyon_discount(self):
        for line in self:
            discount3 = False

            if line.product_id and line.order_id.discount_pricelist_id:
                pricelist = line.order_id.discount_pricelist_id
                price_rule = pricelist.get_product_price_rule(
                    line.product_id, line.product_uom_qty, line.order_id.partner_id
                )

                if price_rule and len(price_rule) == 2 and price_rule[1]:
                    rule = self.env["product.pricelist.item"].browse(price_rule[1])

                    if rule.compute_price == "percentage":
                        discount3 = rule.percent_price
                    elif line.price_unit:
                        price_unit = line.price_unit
                        discount3 = (price_unit - price_rule[0]) / price_unit * 100

            line.discount3 = discount3

    @api.onchange("product_id", "product_uom_qty")
    def onchange_product_id_reset_discount(self):
        self.compute_supplier_promotion()
        self.compute_alcyon_discount()

    @staticmethod
    def apply_discount_pricelist(product, pricelist, price):
        """ Compute a new price by applying *pricelist* on *price*
        """
        if not pricelist:
            return price
        product_temporary = product.with_context(
            override_based_price={product.id: price}, pricelist=pricelist.id
        ).browse(product.id)
        return product_temporary.price

    @api.model
    def _prepare_add_missing_fields(self, values):
        """ Deduce missing required fields from the onchange """
        res = super(SaleOrderLine, self)._prepare_add_missing_fields(values)
        record_values = values.copy()
        record_values.update(res)
        onchange_fields = ["discount2", "discount3"]
        if (
            values.get("order_id")
            and values.get("product_id")
            and any(f not in values for f in onchange_fields)
        ):
            line = self.new(record_values)
            line.onchange_product_id_reset_discount()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res
