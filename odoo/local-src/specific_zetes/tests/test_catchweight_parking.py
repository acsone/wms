# -*- coding: utf-8 -*-

import mock

from .. import constants
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from .zetes_test_classes import ZetesParkingTest


class TestCatchweightParking(ZetesParkingTest):
    def setUp(self):
        super(TestCatchweightParking, self).setUp()

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

        model_name = 'report.stock.refill.arrange'
        report = self.env[model_name].browse(report_id)
        # Create the picking
        self.picking_parking = report.create_picking()

        self.reserve_medicament = self.env['stock.location'].create(
            {
                'name': 'GD80F4',
                'kind': 'reserve',
                'zone': 'G',
                'corridor': 'D',
                'shelf': '80',
                'height': 'F',
                'box': '4',
                'location_id': self.zone_gustave.id,
                'bin_checksum_1': '45',
                'bin_checksum_2': '45',
            }
        )

    def test_01_resu_catchweight(self):
        """
        Move 20 units from the parking to the stock
        :return:
        """

        domain = Catchweight(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )

        pack_op = self.picking_parking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(pack_op.qty_done, 0)
        self.assertEqual(pack_op.pack_lot_ids.qty, 0)

        # Try with a lot
        request_params = Parameters(domain, action='resu')
        request_params.update(
            {
                'lineId': pack_op.id,
                'Usf01': self.lot_product_1.voice_identifier,
                'Usf02': 100,  # Pick 100 unit,
                'Usf03': None,
            }
        )
        domain.resu(request_params)

        self.assertEqual(pack_op.qty_done, 100)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)
        self.assertEqual(pack_op.pack_lot_ids[0].qty, 100)

    def test_02_resu_catchweight(self):
        """
        Move 80 units from the reserve to the stock.
        :return:
        """

        domain = Catchweight(
            self._default_header(), mock.MagicMock(name='Savepoint()')
        )

        pack_op = self.picking_parking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(pack_op.qty_done, 0)
        self.assertEqual(pack_op.pack_lot_ids.qty, 0)

        # Take 80 units
        request_params = Parameters(domain, action='resu')
        request_params.update(
            {
                'lineId': pack_op.id,
                'Usf01': self.lot_product_1.voice_identifier,
                'Usf02': 80,  # Pick 80 unit,
                'Usf03': None,
            }
        )
        domain.resu(request_params)

        self.assertEqual(len(self.picking_parking.pack_operation_ids), 1)
        pack_op = self.picking_parking.pack_operation_ids
        self.assertEqual(len(pack_op), 1)
        self.assertEqual(pack_op.qty_done, 80)

        # Change the state of the move (done by a resu_itemmove)
        pack_op.write({'zetes_state': constants.MOVE_FULL})

        self.env['pack.operation.reserve.rel'].create(
            {
                'pack_operation_id': pack_op.id,
                'lot_id': self.lot_product_1.id,
                'reserve_location_id': self.reserve_medicament.id,
            }
        )

        # Put 20 units in the reserve
        request_params = Parameters(domain, action='resu')
        request_params.update(
            {
                'lineId': pack_op.id,
                'Usf01': self.lot_product_1.voice_identifier,
                'Usf02': 20,  # Pick 20 unit,
                'Usf03': None,
            }
        )
        domain.resu(request_params)

        self.assertEqual(len(self.picking_parking.pack_operation_ids), 2)
        pack_op_bin = self.picking_parking.pack_operation_ids.filtered(
            lambda line: line.location_dest_id == self.location_product_1
        )
        pack_op_reserve = self.picking_parking.pack_operation_ids.filtered(
            lambda line: line.location_dest_id == self.reserve_medicament
        )
        self.assertEqual(len(pack_op_bin), 1)
        self.assertEqual(pack_op_bin.qty_done, 80)
        self.assertEqual(len(pack_op_reserve), 1)
        self.assertEqual(pack_op_reserve.qty_done, 20)
