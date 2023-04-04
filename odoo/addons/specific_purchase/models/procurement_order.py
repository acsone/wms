# -*- coding: utf-8 -*-
# 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
from datetime import datetime

from odoo import _, api, fields, models

MANAGE_DAY_PREFIX = "is_manage_day_"

_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    def make_po(self):
        """
        Update the order date when the procurement update or create a purchase
        order. The new order date must be the datetime of now.
        """
        result = super(ProcurementOrder, self).make_po()

        procurements = self.browse(result)

        pos = procurements.mapped("purchase_id")
        pos.write({"date_order": fields.Datetime.now()})
        with self.env.norecompute():
            # The recompute_discount_values makes direct assignments on line
            # each assignment launch a recompute on the line and on the PO
            # delay the recompute at the end of the discount recompute
            # code to be removed into odoo 13
            pos.mapped("order_line").recompute_discount_values()
        self.recompute()

        return result

    def _get_pol_promotion_supplier(self, po, supplier):
        seller = self.product_id._select_seller(
            partner_id=supplier.name,  # name is a res.partner on supplier.info
            quantity=self.product_qty,
            date=po.date_order and po.date_order[:10],
            uom_id=self.product_id.uom_po_id,
        )
        return seller.discount_purchase or 0.0

    def _prepare_purchase_order_line(self, po, supplier):
        values = super(ProcurementOrder, self)._prepare_purchase_order_line(
            po, supplier
        )
        price_unit_base = values["price_unit"]
        discount_global = po.partner_id.supplier_discount
        promotion_supplier = self._get_pol_promotion_supplier(po, supplier)
        price_unit = self.env["purchase.order.line"]._compute_discount(
            values["price_unit"], discount_global, promotion_supplier
        )
        values.update(
            {
                "price_unit_base": price_unit_base,
                "price_unit": price_unit,
                "discount_global": discount_global,
                "promotion_supplier": promotion_supplier,
            }
        )
        return values
