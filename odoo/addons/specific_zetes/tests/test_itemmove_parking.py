# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_interface import Parameters
from ..tools.domain_itemmove import Itemmove
from .zetes_test_classes import ZetesParkingTest


class TestItemmoveParking(ZetesParkingTest):
    def setUp(self):
        super(TestItemmoveParking, self).setUp()

        report_query = """
        SELECT report.id
        FROM report_stock_refill_arrange AS report
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

        model_name = "report.stock.refill.arrange"
        report = self.env[model_name].browse(report_id)
        # Create the picking
        self.picking_parking = report.create_picking()

    def test_requ_itemmove(self):
        """
        Test REQU Itemmove
        :return:
        """
        domain = Itemmove(self._default_header(), mock.MagicMock(name="Savepoint()"))

        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking_parking.id,
                "itemMoveType": constants.MOVE_TYPE_LOAD,
                "Cri01": None,
            }
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking_parking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking_parking.id))
        self.assertEqual(
            result.moveLineId, "{}_{}".format(pack_op.id, self.lot_product_1.id)
        )
        self.assertEqual(int(result.reqQty), 100)
        self.assertEqual(int(result.effQty), 0)
        self.assertEqual(result.moveStatus, str(constants.MOVE_DEFAULT))
        self.assertEqual(result.productCode, self.product_1.default_code)
        self.assertEqual(result.productDescription, self.product_1.name)
        self.assertFalse(result.productProperty1)
        self.assertFalse(result.productProperty2)
        self.assertEqual(result.productBarcode, self.product_1.barcode or "")
        self.assertEqual(result.scanProductBarcode, "0")

        # Check location
        parking = "{}{}{}{}".format(
            self.parking_medoc.corridor,
            self.parking_medoc.shelf,
            self.parking_medoc.height,
            self.parking_medoc.box,
        )
        self.assertEqual(result.sourceLC1, parking)
        self.assertEqual(result.sourceLC2, self.parking_medoc.corridor or "")
        self.assertEqual(result.sourceLC3, self.parking_medoc.shelf or "")
        self.assertEqual(result.sourceLC4, self.parking_medoc.height or "")
        self.assertEqual(result.sourceLC5, self.parking_medoc.box or "")
        self.assertEqual(result.sourceLCCD, self.parking_medoc.get_checksum() or "")

        # Check dest location
        self.assertEqual(result.destLC1, self.location_product_1.zone)
        self.assertEqual(result.destLC2, self.location_product_1.corridor)
        self.assertEqual(result.destLC3, self.location_product_1.shelf)
        self.assertEqual(result.destLC4, self.location_product_1.height)
        self.assertEqual(result.destLC5, self.location_product_1.box)
        self.assertEqual(result.destLCCD, self.location_product_1.get_checksum())

        # Check lot name
        self.assertEqual(result.Usf01, self.lot_product_1.checksum)

    def test_resu_itempick(self):
        """
        Set the move as done
        :return:
        """
        pack_op = self.picking_parking.pack_operation_product_ids
        pack_op.ensure_one()

        pack_op.pack_lot_ids.write({"qty": 100})
        pack_op.write({"qty_done": 100})

        self.assertEqual(pack_op.qty_done, 100)

        domain = Itemmove(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "moveLineId": pack_op.id,
                "moveStatus": constants.MOVE_DONE,
                "itemMoveType": constants.MOVE_TYPE_LOAD,
            }
        )

        domain.resu(request_params)
        self.assertEqual(pack_op.zetes_state, constants.MOVE_DONE)
        self.assertEqual(pack_op.qty_done, 100)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)
