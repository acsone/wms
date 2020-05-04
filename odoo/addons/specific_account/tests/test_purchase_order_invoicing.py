# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields
from odoo.tests.common import SavepointCase


class TestPurchaseOrderInvoicing(SavepointCase):
    at_install = False
    post_install = True

    @classmethod
    def setUpClass(cls):
        super(TestPurchaseOrderInvoicing, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {"name": u"TEST", "supplier": True, "ref": "42"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": u"TEST", "type": "consu", "purchase_method": "receive"}
        )
        today = fields.Date.today()
        po_vals = {
            "partner_id": cls.partner.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": u"Line 1",
                        "product_id": cls.product.id,
                        "product_qty": 10,
                        "product_uom": cls.product.uom_id.id,
                        "price_unit": 10,
                        "date_planned": today,
                    },
                )
            ],
        }
        cls.order = cls.env["purchase.order"].create(po_vals)

    def _process_picking(self, picking):
        picking.assign_operator()
        for pack in picking.pack_operation_product_ids:
            # Receive only partial qty
            pack.qty_done = pack.product_qty / 2
        # test_mode context key to bypass the 'Goods Received Note'
        # check from the 'specific_stock' module
        picking.with_context(test_mode=True).do_transfer()
        picking.invalidate_cache()

    def test_purchase_order_invoicing_prepayment(self):
        """With prepayment on the order, we should invoice all the
        ordered quantity.
        """
        self.order.prepayment = True
        self.order.button_confirm()
        picking = self.order.picking_ids
        self._process_picking(picking)

        invoice_vals = {"partner_id": self.partner.id}
        invoice = self.env["account.invoice"].create(invoice_vals)
        # Encode purchase order lines
        invoice.purchase_id = self.order
        invoice.purchase_order_change()
        line_product = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.product
        )
        self.assertTrue(line_product)
        self.assertEqual(line_product.quantity, 10)
        self.assertEqual(line_product.price_unit, 10)
        self.assertEqual(line_product.purchase_line_qty_received, 10)
        self.assertEqual(line_product.purchase_line_product_qty, 10)
        nb_inv_lines = len(invoice.invoice_line_ids)
        # Encode again and check that the number of invoice lines didn't change
        invoice.purchase_id = self.order
        invoice.purchase_order_change()
        self.assertEqual(nb_inv_lines, len(invoice.invoice_line_ids))
        line_product = invoice.invoice_line_ids.filtered(
            lambda l: l.product_id == self.product
        )
        self.assertEqual(line_product.quantity, 10)
        self.assertEqual(line_product.price_unit, 10)
        self.assertEqual(line_product.purchase_line_qty_received, 10)
        self.assertEqual(line_product.purchase_line_product_qty, 10)
