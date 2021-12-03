# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.tests.common import SavepointCase


class TestAutoCancelUnavailableQty(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestAutoCancelUnavailableQty, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {"name": "TEST CUSTOMER", "ref": "4929752", "customer": True}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "TEST", "default_code": "TEST", "type": "product"}
        )
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "date_order": "2018-01-29",
                "sale_channel": "web",
            }
        )

    def update_product_stock_qty(self, product, qty):
        wiz = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": qty,
                "location_id": self.env.ref("stock.stock_location_stock").id,
            }
        )
        wiz.change_product_qty()

    def test_option_enabled_qty_unavailable(self):
        """Auto-cancel unavailable qty feature enabled with unavailable qty

        The ordered qty is then shrinked to the available qty in stock to avoid
        a shipping backorder, the undelivered qty is stored as canceled qty.
        """
        self.partner.auto_cancel_unavailable_qty_sold = True
        self.update_product_stock_qty(self.product, 6)
        line = self.order.order_line.create(
            {
                "order_id": self.order.id,
                "sequence": 1,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 10,
            }
        )
        self.assertEqual(line.product_id.immediately_usable_qty, 6)
        self.assertEqual(line.product_qty_canceled, 0)
        self.assertEqual(line.product_qty_unavailable, 4)
        self.order.action_confirm()
        # the uom qty should not be change cause (it's should include the
        # cancel qty) ALCYN-2359
        self.assertEqual(line.product_uom_qty, 10)
        self.assertEqual(line.product_qty_canceled, 4)
        # ALCYN-2359 the backorders must keep their value
        self.assertEqual(line.product_qty_unavailable, 4)
        proc = line.procurement_ids.filtered(lambda r: r.state != "cancel")
        self.assertEqual(proc.product_qty, 6)

    def test_option_enabled_qty_available(self):
        """Auto-cancel unavailable qty feature enabled with enough qty in stock

        The whole ordered qty can be shipped (no cancel qty).
        """
        self.partner.auto_cancel_unavailable_qty_sold = True
        self.update_product_stock_qty(self.product, 10)
        line = self.order.order_line.create(
            {
                "order_id": self.order.id,
                "sequence": 1,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 10,
            }
        )
        self.assertEqual(line.product_id.immediately_usable_qty, 10)
        self.assertEqual(line.product_qty_canceled, 0)
        self.assertEqual(line.product_qty_unavailable, 0)
        self.order.action_confirm()
        self.assertEqual(line.product_uom_qty, 10)
        self.assertEqual(line.product_qty_canceled, 0)
        self.assertEqual(line.product_qty_unavailable, 0)

    def test_option_disabled(self):
        """Auto-cancel unavailable qty feature disabled:

        whatever the ordered qty and the available qty are at first, the
        ordered qty doesn't get updated when the order is confirmed.
        """
        self.partner.auto_cancel_unavailable_qty_sold = False
        self.update_product_stock_qty(self.product, 6)
        line = self.order.order_line.create(
            {
                "order_id": self.order.id,
                "sequence": 1,
                "name": self.product.name,
                "product_id": self.product.id,
                "product_uom_qty": 10,
            }
        )
        self.assertEqual(line.product_id.immediately_usable_qty, 6)
        self.assertEqual(line.product_qty_canceled, 0)
        self.assertEqual(line.product_qty_unavailable, 4)
        self.order.action_confirm()
        self.assertEqual(line.product_uom_qty, 10)
        self.assertEqual(line.product_qty_canceled, 0)
        self.assertEqual(line.product_qty_unavailable, 4)
