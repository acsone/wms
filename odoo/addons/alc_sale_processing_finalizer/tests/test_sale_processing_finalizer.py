# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date, timedelta

from freezegun import freeze_time

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestCron(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        today = date.today()
        with freeze_time(today - timedelta(days=100)):
            cls.warehouse_1 = cls.env.ref("stock.warehouse0")
            cls.warehouse_1.write(
                {
                    "name": "Test Warehouse",
                    "reception_steps": "one_step",
                    "delivery_steps": "pick_ship",
                    "code": "BWH",
                }
            )
            cls.SaleOrder = cls.env["sale.order"]
            cls.partner = cls.env["res.partner"].create({"name": "Unittest partner"})
            cls.p1 = cls.env["product.product"].create(
                {"name": "Unittest P1", "type": "product"}
            )
            cls.p2 = cls.env["product.product"].create(
                {"name": "Unittest P2", "type": "product"}
            )
            cls.p3 = cls.env["product.product"].create(
                {"name": "P3", "type": "product"}
            )
            cls.p4 = cls.env["product.product"].create(
                {"name": "P4", "type": "product"}
            )
            cls.so_after_3months_to_purge = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "warehouse_id": cls.warehouse_1.id,
                    "order_line": [
                        Command.create(
                            {
                                "name": cls.p1.name,
                                "product_id": cls.p1.id,
                                "product_uom_qty": 2,
                                "product_uom": cls.p1.uom_id.id,
                                "price_unit": 1,
                            },
                        )
                    ],
                }
            )
            cls.so_draft_auto_finalize = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "warehouse_id": cls.warehouse_1.id,
                    "order_line": [
                        Command.create(
                            {
                                "name": cls.p3.name,
                                "product_id": cls.p3.id,
                                "product_uom_qty": 1,
                                "product_uom": cls.p3.uom_id.id,
                                "price_unit": 1,
                            },
                        )
                    ],
                }
            )
            cls.so_after_3months_to_keep = cls.SaleOrder.create(
                {
                    "partner_id": cls.partner.id,
                    "warehouse_id": cls.warehouse_1.id,
                    "auto_finalize_processing": False,
                    "order_line": [
                        Command.create(
                            {
                                "name": cls.p2.name,
                                "product_id": cls.p2.id,
                                "product_uom_qty": 6,
                                "product_uom": cls.p2.uom_id.id,
                                "price_unit": 1,
                            },
                        )
                    ],
                }
            )
            cls.so_after_3months_to_purge.action_confirm()
            cls.so_after_3months_to_purge.action_done()  # lock the so
            cls.so_after_3months_to_keep.action_confirm()
            cls.so_after_3months_to_keep.action_done()  # lock the so
        cls.so_auto_finalize = cls.SaleOrder.create(
            {
                "partner_id": cls.partner.id,
                "warehouse_id": cls.warehouse_1.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p4.name,
                            "product_id": cls.p4.id,
                            "product_uom_qty": 7,
                            "product_uom": cls.p4.uom_id.id,
                            "price_unit": 1,
                        },
                    )
                ],
            }
        )
        cls.so_auto_finalize.action_confirm()
        cls.so_auto_finalize.action_done()

    def test_cron_method(self):
        """
        Data: 1 so (old to_purge) with auto_finalize_processing set and confirmed.

              1 so (old to_keep) with auto_finalize_processing not set and confirmed..
              1 so (olf draft to keep) with auto_finalize_processing set.
              1 so (young to keep) with auto_finalize_processing set and confirmed.
        case: trigger the cron method: cancel_sales_bo_gt_3months
        result: product_qty_canceled is > 0 and product_qty_remains_to_deliver = 0 for
                the so to_purge
                product_qty_canceled is = 0 and product_qty_remains_to_deliver > 0 for
                the so's to_keep
        """
        self.env["sale.order"].cancel_sales_bo_gt_3months()

        # Check that quantities for SO to purge have indeed been purged
        self.assertEqual(
            self.so_after_3months_to_purge.order_line.product_qty_canceled, 2
        )
        self.assertEqual(
            self.so_after_3months_to_purge.order_line.product_qty_remains_to_deliver, 0
        )
        # check that SO to purge pickings are cancelled
        self.assertEqual(
            self.so_after_3months_to_purge.picking_ids.mapped("state"),
            ["cancel", "cancel"],
        )

        # Check that quantities for SO to keep are still there
        self.assertEqual(
            self.so_after_3months_to_keep.order_line.product_qty_canceled, 0
        )
        self.assertEqual(
            self.so_after_3months_to_keep.order_line.product_qty_remains_to_deliver, 6
        )

        # Check that quantities for SO draft auto finalize are still there
        self.assertEqual(self.so_draft_auto_finalize.order_line.product_qty_canceled, 0)
        self.assertEqual(
            self.so_draft_auto_finalize.order_line.product_qty_remains_to_deliver, 1
        )

        # Check that quantities for SO 1 month auto finalize are still there
        self.assertEqual(self.so_auto_finalize.order_line.product_qty_canceled, 0)
        self.assertEqual(
            self.so_auto_finalize.order_line.product_qty_remains_to_deliver, 7
        )

    def test_long_term_carrier(self):
        """
        Data: 1 so (to_purge) with auto_finalize_processing set and 1 so (to_keep).

              without. The so to_purge has also a long term delivery carrier set.
              Both so's are confirmed and done.
        case: trigger the cron method: cancel_sales_bo_gt_3months
        result: product_qty_canceled is = 0 and product_qty_remains_to_deliver > 0 for
                the so to_purge
                product_qty_canceled is = 0 and product_qty_remains_to_deliver > 0 for
                the so to_keep
        """
        carrier = self.env.ref("delivery.delivery_carrier")
        carrier.is_long_term_delivery = True
        self.so_after_3months_to_purge.carrier_id = carrier.id

        self.env["sale.order"].cancel_sales_bo_gt_3months()

        # Check that quantities for SO to purge have not been purged
        self.assertEqual(
            self.so_after_3months_to_purge.order_line.product_qty_canceled, 0
        )
        self.assertEqual(
            self.so_after_3months_to_purge.order_line.product_qty_remains_to_deliver, 2
        )

        # Check that quantities for SO to keep are still there
        self.assertEqual(
            self.so_after_3months_to_keep.order_line.product_qty_canceled, 0
        )
        self.assertEqual(
            self.so_after_3months_to_keep.order_line.product_qty_remains_to_deliver, 6
        )
