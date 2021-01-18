# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_interface import Parameters
from ..tools.domain_itemmove import Itemmove
from .zetes_test_classes import ZetesReserveTest


class TestItemmoveReserve(ZetesReserveTest):
    def setUp(self):
        super(TestItemmoveReserve, self).setUp()

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

    def test_requ_itemmove(self):
        """

        :return:
        """
        domain = Itemmove(self._default_header(), mock.MagicMock(name="Savepoint()"))

        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking_reserve.id,
                "itemMoveType": constants.MOVE_TYPE_PUT,
                "Cri01": None,
            }
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking_reserve.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking_reserve.id))
        self.assertEqual(
            result.moveLineId, u"{}_{}".format(pack_op.id, self.lot_product_1.id)
        )
        self.assertEqual(int(result.reqQty), 20)
        self.assertEqual(int(result.effQty), 0)
        self.assertEqual(result.moveStatus, str(constants.MOVE_DEFAULT))
        self.assertEqual(result.productCode, self.product_1.default_code)
        self.assertEqual(result.productDescription, self.product_1.name)
        self.assertFalse(result.productProperty1)
        self.assertFalse(result.productProperty2)
        self.assertEqual(result.productBarcode, self.product_1.barcode or "")
        self.assertEqual(result.scanProductBarcode, "0")

        # Check location
        self.assertEqual(result.sourceLC1, self.reserve_medoc.zone)
        self.assertEqual(result.sourceLC2, self.reserve_medoc.corridor)
        self.assertEqual(result.sourceLC3, self.reserve_medoc.shelf)
        self.assertEqual(result.sourceLC4, self.reserve_medoc.height)
        self.assertEqual(result.sourceLC5, self.reserve_medoc.box)
        self.assertEqual(result.sourceLCCD, self.reserve_medoc.get_checksum())

        # Currently there is a bug with the method to create
        # the picking from the reserve
        # # Check dest location
        # self.assertEqual(result.destLC1, self.location_product_1.zone)
        # self.assertEqual(result.destLC2, self.location_product_1.corridor)
        # self.assertEqual(result.destLC3, self.location_product_1.shelf)
        # self.assertEqual(result.destLC4, self.location_product_1.height)
        # self.assertEqual(result.destLC5, self.location_product_1.box)
        # self.assertEqual(result.destLCCD,
        #                  self.location_product_1.get_checksum())

        # Check lot name
        self.assertEqual(result.Usf01, self.lot_product_1.checksum)

    def test_resu_itempick(self):
        """
        Take all 20 units of product 1
        :return:
        """
        pack_op = self.picking_reserve.pack_operation_product_ids
        pack_op.ensure_one()

        pack_op.pack_lot_ids.write({"qty": 20})
        pack_op.write({"qty_done": 20})

        self.assertEqual(pack_op.qty_done, 20)

        domain = Itemmove(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "moveLineId": pack_op.id,
                "moveStatus": constants.MOVE_DONE,
                "itemMoveType": constants.MOVE_TYPE_PUT,
            }
        )

        domain.resu(request_params)
        self.assertEqual(pack_op.zetes_state, constants.MOVE_DONE)
        self.assertEqual(pack_op.qty_done, 20)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)
        self.assertEqual(self.picking_reserve.state, "done")
