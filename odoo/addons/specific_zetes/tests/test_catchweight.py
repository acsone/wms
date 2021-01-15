# -*- coding: utf-8 -*-
from datetime import datetime

import mock
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tools import mute_logger

from .. import constants
from ..tools.domain_catchweight import Catchweight
from ..tools.domain_interface import Parameters
from .zetes_test_classes import ZetesTest


class TestCatchweight(ZetesTest):
    def test_requ_catchweight(self):
        """
        The method requ on catchweight is not used.
        :return:
        """
        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": self.picking.pack_operation_product_ids.id,
                "productCode": self.product_1.default_code,
                "lotNumber": self.lot_product_1.name,
                "effQty": 10,
            }
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))

    @mute_logger("odoo.addons.specific_zetes.tools.domain_interface")
    def test_requ_catchweight_wrong_pack(self):
        """
        Check that the method return an error code if we provide a wrong
        pack operation id
        :return:
        """
        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": -1,
                "productCode": self.product_1.default_code,
                "lotNumber": self.lot_product_1.name,
                "effQty": 10,
            }
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))

    def test_requ_catchweight_deleted_pack(self):
        """
        Check that the method return an error code if we provide a deleted
        pack operation id and that a zettes loger is created for the related
        picking to log this event
        :return:
        """
        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()
        pack_op_id = pack_op.id
        pack_op.unlink()

        self.assertFalse(self.picking.is_zetes_error)
        request_params.update(
            {
                "groupNum": self.picking.id,
                "pickLineId": pack_op_id,
                "productCode": self.product_1.default_code,
                "lotNumber": self.lot_product_1.name,
                "effQty": 10,
            }
        )
        result_str = domain.requ(request_params)
        self.assertTrue(self.picking.is_zetes_error)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))

    def test_resu_catchweight(self):
        """
        Change the picked quantity on the pack operation
        :return:
        """

        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(pack_op.qty_done, 0)
        self.assertEqual(pack_op.pack_lot_ids.qty, 0)

        # Try with a lot
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "lineId": pack_op.id,
                "Usf01": self.lot_product_1.voice_identifier,
                "Usf02": 5,  # Pick 5 unit,
                "Usf03": None,
            }
        )
        domain.resu(request_params)

        self.assertEqual(pack_op.qty_done, 5)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)
        self.assertEqual(pack_op.pack_lot_ids[0].qty, 5)

        # Create a new lot and pick in this lot
        two_years = datetime.now() + relativedelta(years=1)
        second_lot = self.env["stock.production.lot"].create(
            {
                "name": "000000002",
                "product_id": self.product_1.id,
                "removal_date": fields.Datetime.to_string(two_years),
            }
        )

        second_request_params = Parameters(domain, action="resu")
        second_request_params.update(
            {
                "lineId": pack_op.id,
                "Usf01": second_lot.voice_identifier,
                "Usf02": 5,  # Pick 5 unit in a second lot,
                "Usf03": None,
            }
        )
        domain.resu(second_request_params)

        self.assertEqual(pack_op.qty_done, 10)
        self.assertEqual(len(pack_op.pack_lot_ids), 2)
        self.assertEqual(pack_op.pack_lot_ids[1].qty, 5)

    @mute_logger("odoo.addons.specific_zetes.tools.domain_interface")
    def test_resu_catchweight_wrong_pack_op(self):
        """
        Provides a wrong pack operation
        :return:
        """
        self.product_1.write({"tracking": "none"})

        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {"lineId": -1, "Usf01": None, "Usf02": 5, "Usf03": None}  # Pick 5 unit,
        )
        self.assertIsNone(domain.resu(request_params))

    def test_resu_catchweight_without_lot(self):
        """
        Set the picked quantity on a pack operation without a lot
        :return:
        """
        self.product_1.write({"tracking": "none"})

        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(pack_op.qty_done, 0)

        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "lineId": pack_op.id,
                "Usf01": None,
                "Usf02": 5,  # Pick 5 unit,
                "Usf03": None,
            }
        )
        domain.resu(request_params)

        self.assertEqual(pack_op.qty_done, 5)

    @mute_logger("odoo.addons.specific_zetes.tools.domain_catchweight")
    def test_resu_catchweight_check_picked_quantity(self):
        """
        Pick 15 units (the max allowed is 10 units)
        :return:
        """

        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))

        pack_op = self.picking.pack_operation_product_ids
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

        self.assertEqual(pack_op.qty_done, 10)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)
        self.assertEqual(pack_op.pack_lot_ids[0].qty, 10)

        log = self.env["zetes.logger"].search(
            [("picking_id", "=", self.picking.id), ("operation_id", "=", pack_op.id)]
        )
        self.assertEqual(len(log), 1)
        self.assertEqual(log.error_type, "human")

    @mute_logger("odoo.addons.specific_zetes.tools.domain_catchweight")
    def test_resu_catchweight_check_actual_stock(self):
        """
        Change the picked quantity on the pack operation
        :return:
        """

        domain = Catchweight(self._default_header(), mock.MagicMock(name="Savepoint()"))

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        # The stock should be 90
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "lineId": pack_op.id,
                "Usf01": self.lot_product_1.voice_identifier,
                "Usf02": 0,
                "Usf03": "90",
            }
        )
        domain.resu(request_params)

        log = self.env["zetes.logger"].search(
            [("picking_id", "=", self.picking.id), ("operation_id", "=", pack_op.id)]
        )

        self.assertEqual(len(log), 0)

        # But not 93
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {
                "lineId": pack_op.id,
                "Usf01": self.lot_product_1.voice_identifier,
                "Usf02": 0,
                "Usf03": "93",
            }
        )
        domain.resu(request_params)

        log = self.env["zetes.logger"].search(
            [("picking_id", "=", self.picking.id), ("operation_id", "=", pack_op.id)]
        )

        self.assertEqual(len(log), 1)
        self.assertEqual(log.error_type, "human")
