# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields

from .. import constants
from .zetes_test_classes import ZetesTest, DEFAULT_HEADER
from ..tools.domain_interface import Parameters
from ..tools.domain_catchweight import Catchweight


class TestCatchweight(ZetesTest):

    def test_requ_catchweight(self):
        """
        The method requ on catchweight is not used.
        :return:
        """
        domain = Catchweight(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'groupNum': self.picking.id,
            'pickLineId': self.picking.pack_operation_product_ids.id,
            'productCode': self.product_1.default_code,
            'lotNumber': self.lot_product_1.name,
            'effQty': 10,
        })

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

    def test_resu_catchweight(self):
        """
        Change the picked quantity on the pack operation
        :return:
        """

        domain = Catchweight(DEFAULT_HEADER, request_overwrite=self)

        move = self.picking.pack_operation_product_ids
        move.ensure_one()

        self.assertEqual(move.qty_done, 0)
        self.assertEqual(move.pack_lot_ids.qty, 0)

        # Try with a lot
        request_params = Parameters(domain, action='resu')
        request_params.update({
            'lineId': move.id,
            'Usf01': self.lot_product_1.checksum,
            'Usf02': 5,  # Pick 5 unit
        })
        domain.resu(request_params)

        self.assertEqual(move.qty_done, 5)
        self.assertEqual(len(move.pack_lot_ids), 1)
        self.assertEqual(move.pack_lot_ids[0].qty, 5)

        # Create a new lot and pick in this lot
        two_years = datetime.now() + relativedelta(years=1)
        second_lot = self.env['stock.production.lot'].create({
            'name': '000000002',
            'product_id': self.product_1.id,
            'life_date': fields.Datetime.to_string(two_years),
        })

        second_request_params = Parameters(domain, action='resu')
        second_request_params.update({
            'lineId': move.id,
            'Usf01': second_lot.checksum,
            'Usf02': 5,  # Pick 5 unit in a second lot
        })
        domain.resu(second_request_params)

        self.assertEqual(move.qty_done, 10)
        self.assertEqual(len(move.pack_lot_ids), 2)
        self.assertEqual(move.pack_lot_ids[1].qty, 5)

    def test_resu_catchweight_without_lot(self):
        """
        Set the picked quantity on a pack operation without a lot
        :return:
        """
        self.product_1.write({
            'tracking': 'none'
        })

        domain = Catchweight(DEFAULT_HEADER, request_overwrite=self)

        move = self.picking.pack_operation_product_ids
        move.ensure_one()

        self.assertEqual(move.qty_done, 0)

        request_params = Parameters(domain, action='resu')
        request_params.update({
            'lineId': move.id,
            'Usf01': None,
            'Usf02': 5,  # Pick 5 unit
        })
        domain.resu(request_params)

        self.assertEqual(move.qty_done, 5)
