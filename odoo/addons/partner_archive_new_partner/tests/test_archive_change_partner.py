# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests import common


@common.at_install(False)
@common.post_install(True)
class TestPartner(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestPartner, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner1 = cls.env["res.partner"].create({"name": "Partner1"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Partner2"})
        cls.product = cls.env.ref("product.product_product_8")
        cls.account_type = cls.env.ref("account.data_account_type_receivable")
        cls.profit_acc_id = cls.env.ref("account.data_account_type_revenue")
        cls.payment_term = cls.env.ref("account.account_payment_term_advance")
        cls.account_id = cls.env["account.account"].create(
            {
                "name": "Receive account",
                "code": "440000_demo",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.profit_acc_id = cls.env["account.account"].create(
            {
                "name": "Revenue account",
                "code": "702",
                "user_type_id": cls.profit_acc_id.id,
            }
        )
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Sales Journal - (test)",
                "code": "TSAJ",
                "type": "sale",
                "refund_sequence": True,
            }
        )
        cls.partner1.property_account_receivable_id = cls.account_id
        cls.partner1.property_account_payable_id = cls.profit_acc_id

    def setUp(self):
        super(TestPartner, self).setUp()

        self.saleorder = self.env["sale.order"].create(
            {
                "partner_id": self.partner1.id,
                "partner_invoice_id": self.partner1.id,
                "partner_shipping_id": self.partner1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Product Test",
                            "product_id": self.product.id,
                            "product_uom_qty": 1,
                            "product_uom": self.env.ref("product.product_uom_unit").id,
                            "price_unit": 100.0,
                        },
                    )
                ],
            }
        )
        self.invoice = self.env["account.invoice"].create(
            {
                "name": "Test invoice",
                "partner_id": self.partner1.id,
                "type": "out_invoice",
                "payment_term_id": self.payment_term.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test line",
                            "product_id": self.product.id,
                            "quantity": 10.0,
                            "price_unit": 50.0,
                            "account_id": self.profit_acc_id.id,
                        },
                    )
                ],
            }
        )
        self.picking = self.env["stock.picking"].create(
            {
                "location_id": self.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": self.env.ref("stock.stock_location_stock").id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "partner_id": self.partner1.id,
            }
        )

    def test_writing_sale_order_partner(self):
        self.partner1.active = True
        wizard_data = self.partner1.archive_partner()
        context = wizard_data["context"]
        context["active_id"] = self.partner1.id
        self.env[wizard_data["res_model"]].with_context(context).create(
            {"new_partner_id": self.partner2.id}
        ).action_confirm()
        self.assertEqual(self.saleorder.partner_id, self.partner2)
        self.assertEqual(self.saleorder.partner_invoice_id, self.partner2)
        self.assertEqual(self.saleorder.partner_shipping_id, self.partner2)

    def test_writing_invoice_partner(self):
        self.partner1.active = True
        self.invoice.action_invoice_open()
        self.assertEqual(self.invoice.state, "open")
        wizard_data = self.partner1.archive_partner()
        context = wizard_data["context"]
        context["active_id"] = self.partner1.id
        self.env[wizard_data["res_model"]].with_context(context).create(
            {"new_partner_id": self.partner2.id}
        ).action_confirm()
        self.assertEqual(self.invoice.partner_id, self.partner2)
        # move still keeps old partner
        self.assertEqual(
            self.invoice.move_id.mapped("line_ids.partner_id"), self.partner1
        )

    def test_writing_delivery_order_partner(self):
        self.partner1.active = True
        wizard_data = self.partner1.archive_partner()
        context = wizard_data["context"]
        context["active_id"] = self.partner1.id
        self.env[wizard_data["res_model"]].with_context(context).create(
            {"new_partner_id": self.partner2.id}
        ).action_confirm()
        self.assertEqual(self.picking.partner_id, self.partner2)
