# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields

from odoo.addons.product.models.product_pricelist import Pricelist
from odoo.addons.sale.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):

    supplier_promotion_allowed = fields.Boolean(
        string="Supplier promotion allowed",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )
    discount_pricelist_ids = fields.Many2many[Pricelist](
        relation="order_discount_pricelist_rel",
        column1="order_id",
        column2="pricelist_id",
        string="Alcyon Discount",
        readonly=True,
        states={"draft": [("readonly", False)], "sent": [("readonly", False)]},
    )

    @api.model
    def create(self, vals):
        """Fills discount pricelist field (if it is not).

        based on partner configuration.
        """
        # Since they don't have a column_type, discount_pricelist_ids and order_line
        # are computed afterwards, in an arbitrary order.
        # Because of that, the discounts on lines could be wrong.
        # To force the correct order, we do the order_line write in a second step.
        # Same problem applies to write.
        partner_model = self.env["res.partner"]
        partner_id = vals.get("partner_id")
        if partner_id:
            partner = partner_model.browse(partner_id)
            if "discount_pricelist_ids" not in vals:
                pricelists = partner.discount_pricelist_ids
                if pricelists:
                    vals["discount_pricelist_ids"] = [(6, 0, pricelists.ids)]
            if "supplier_promotion_allowed" not in vals:
                vals[
                    "supplier_promotion_allowed"
                ] = partner.supplier_promotion_sale_allowed
        order_lines = vals.pop("order_line", [])
        res = super().create(vals)
        if order_lines:
            res.write({"order_line": order_lines})
        return res

    def write(self, vals):
        # same issue as with create
        order_lines = False
        if vals.get("order_line") and vals.get("discount_pricelist_ids"):
            order_lines = vals.pop("order_line")
        res = super().write(vals)
        if order_lines:
            self.write({"order_line": order_lines})
        return res

    @api.onchange("partner_id")
    def onchange_partner_id_discount_pricelist(self):
        """Update promotion and discount pricelist fields.

        when partner_id is updated.
        """
        self.supplier_promotion_allowed = (
            self.partner_id.supplier_promotion_sale_allowed
        )
        pricelists = self.partner_id.discount_pricelist_ids
        self.discount_pricelist_ids = [(6, 0, pricelists.ids)]

    @api.onchange("supplier_promotion_allowed")
    def onchange_supplier_promotion_allowed(self):
        self.order_line.compute_supplier_promotion()

    @api.onchange("discount_pricelist_ids")
    def onchange_discount_pricelist_ids(self):
        self.order_line.compute_alcyon_discount()

    def action_update_prices(self):
        for order in self:
            if order.discount_pricelist_ids != order.partner_id.discount_pricelist_ids:
                order.write(
                    {
                        "discount_pricelist_ids": [
                            Command.set(order.partner_id.discount_pricelist_ids.ids)
                        ]
                    }
                )
            order.order_line.onchange_product_id_reset_discount()
        return super().action_update_prices()
