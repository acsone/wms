# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from dateutil.relativedelta import relativedelta

from .common import TestSaleProcessingFinalizerComon


class TestCron(TestSaleProcessingFinalizerComon):
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

        # Check that that already canceled BOs don't rise again
        lines = self.env["sale.order.line"].search(
            [
                ("product_qty_remains_to_deliver", ">", 0),
                ("product_type", "in", ["consu", "product"]),
                ("is_consignment", "=", False),
                (
                    "date_order",
                    "<",
                    (datetime.datetime.today() - relativedelta(months=3)).date(),
                ),
            ]
        )
        lines = self.env["sale.order"]._filter_sale_order_lines_to_cancel(lines)
        self.assertNotIn(lines, self.so_after_3months_to_purge.order_line)

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
