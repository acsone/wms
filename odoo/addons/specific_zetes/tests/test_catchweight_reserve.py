# -*- coding: utf-8 -*-
import mock

from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from .zetes_test_classes import ZetesReserveTest


class TestCatchweightReserve(ZetesReserveTest):
    def setUp(self):
        super(TestCatchweightReserve, self).setUp()

        report_query = """
        SELECT report.id
        FROM report_stock_refill_reassort AS report
          LEFT JOIN stock_location ON stock_location.id = report.location_id
          LEFT JOIN picking_zone
            ON stock_location.picking_zone_id = picking_zone.id
        WHERE report.product_id = %s
          AND picking_zone.code = %s
        LIMIT 1
        """
        self.env.cr.execute(
            report_query, (self.product_1.id, self.picking_zone_medoc.code)
        )
        result = self.env.cr.fetchone()

        self.assertTrue(result)
        report_id = result[0]

        model_name = "report.stock.refill.reassort"
        report = self.env[model_name].browse(report_id)
        # Create the picking
        self.picking_reserve = report.create_picking()

    def test_01_resu_catchweight(self):
        """
        Move 20 units from the reserve to the stock
        :return:
        """

        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))

        pack_op = self.picking_reserve.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(pack_op.qty_done, 0)
        self.assertEqual(pack_op.pack_lot_ids.qty, 0)

        # Try with a lot
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "lineId": pack_op.id,
                "Usf01": self.lot_product_1.voice_identifier,
                "Usf02": 20,  # Pick 20 unit,
                "Usf03": None,
            }
        )
        domain.resu(request_params)

        self.assertEqual(pack_op.qty_done, 20)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)
        self.assertEqual(pack_op.pack_lot_ids[0].qty, 20)

    def test_02_resu_catchweight(self):
        """
        Move 15 units from the reserve to the stock.
        5 units lefts in the reverse
        :return:
        """

        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))

        pack_op = self.picking_reserve.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(pack_op.qty_done, 0)
        self.assertEqual(pack_op.pack_lot_ids.qty, 0)

        # Try with a lot
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "lineId": pack_op.id,
                "Usf01": self.lot_product_1.voice_identifier,
                "Usf02": 15,  # Pick 15 unit,
                "Usf03": None,
            }
        )
        domain.resu(request_params)

        self.assertEqual(len(self.picking_reserve.pack_operation_ids), 2)
        pack_op_bin = self.picking_reserve.pack_operation_ids.filtered(
            lambda line: line.qty_done == 15
        )
        pack_op_reserve = self.picking_reserve.pack_operation_ids.filtered(
            lambda line: line.qty_done == 5
        )
        self.assertEqual(len(pack_op_bin), 1)
        self.assertEqual(len(pack_op_reserve), 1)
