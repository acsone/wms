# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product.models.product_pricelist_item import PricelistItem
from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):

    discount_item_id = fields.Many2one[PricelistItem](
        compute="_compute_discount_item_id", store=True
    )
    # This field purpose is only to prevent the computation of the supplier's and alcyon's
    # promotions at record creation when promotion2 or promotion3 values are provided.
    # `store` attribute is set to `False` in order to ensure that its effect is limited
    # to the create call_kw call from the client.
    skip_reset_discount = fields.Boolean(store=False)

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        # As non stored fields are not populated at creation, passing it through the vals
        # does not work, and we unfortunately need to set the value after the super() call.
        result.filtered(
            lambda sol: sol.discount2 or sol.discount3
        ).skip_reset_discount = True
        return result

    def compute_supplier_promotion(self):
        for line in self:
            discount2 = False

            condition = line.product_id and line.order_id.supplier_promotion_allowed
            if condition:
                seller = line.product_id._select_seller(
                    partner_id=False,
                    quantity=line.product_uom_qty,
                    date=line.order_id.date_order.date(),
                    uom_id=line.product_uom,
                )

                if seller and self._is_supplier_promotion_suiteable(seller):
                    discount2 = seller.discount_sale
            line.discount2 = discount2

    def _is_supplier_promotion_suiteable(self, seller):
        return (
            not seller.only_for_veterinaries
            or self.order_id.partner_id.partner_type == "veterinary"
        )

    @api.depends("order_id.discount_pricelist_ids", "product_id", "product_uom_qty")
    def _compute_discount_item_id(self):
        for line in self:
            pricelists = line.order_id.discount_pricelist_ids._origin
            # we don't use UOMs, if that changes then apply it here:
            if not pricelists:
                continue
            line.discount_item_id = line.product_id._get_best_applicable_pricelist_item(
                line.order_id.date_order,
                quantity=line.product_uom_qty or 1,
                pricelists=line.order_id.discount_pricelist_ids._origin,
                currency=line.currency_id,
            )
        records_to_skip = self.filtered("skip_reset_discount")
        # We limit `skip_reset_discount` scope by setting it back directly to False.
        records_to_skip.skip_reset_discount = False
        (self - records_to_skip).onchange_product_id_reset_discount()

    def compute_alcyon_discount(self):
        for line in self:
            discount3 = False
            if line.product_id and line.discount_item_id:
                rule = line.discount_item_id
                if rule.compute_price == "percentage":
                    discount3 = rule.percent_price
                elif line.price_unit:
                    price_unit = line.price_unit
                    item_price = rule._compute_price(
                        line.product_id,
                        line.product_uom_qty,
                        line.product_uom,
                        line.order_id.date_order or fields.Date.context_today(line),
                    )
                    discount3 = (price_unit - item_price) / price_unit * 100

            line.discount3 = discount3

    @api.onchange("discount_item_id")
    def onchange_product_id_reset_discount(self):
        self.compute_supplier_promotion()
        self.compute_alcyon_discount()

    @staticmethod
    def apply_discount_pricelist(product, pricelist, price):
        """Compute a new price by applying *pricelist* on *price*."""
        if not pricelist:
            return price
        product_temporary = product.with_context(
            override_based_price={product.id: price}, pricelist=pricelist.id
        ).browse(product.id)
        return product_temporary.price

    @api.model
    def _prepare_add_missing_fields(self, values):
        """Deduce missing required fields from the onchange."""
        res = super()._prepare_add_missing_fields(values)
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
