# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_interface import Parameters
from ..tools.domain_location import Location
from .zetes_test_classes import ZetesTest


class TestLocation(ZetesTest):
    def test_requ_location(self):
        """
        :return:
        """
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        domain = Location(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "lineId": pack_op.id,
                "Cri01": self.location_product_1.zone,
                "Cri02": self.location_product_1.corridor,
                "Cri03": self.location_product_1.shelf,
                "Cri04": self.location_product_1.height,
                "Cri05": self.location_product_1.box,
                "Cri07": self.lot_product_1.checksum,
            }
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.productCode, self.product_1.default_code)
        self.assertEqual(result.productDescription, self.product_1.name)
        self.assertEqual(result.quantity, "100.0")
        # If we use a demo database for this test, the result will be 100
        # but if you use an Alcyon DB, the result is 90. It is a problem
        # with warehouse configuration
        # self.assertEqual(result.Usf07, '90.0')

        # Check location
        self.assertEqual(result.lC1, self.location_product_1.zone)
        self.assertEqual(result.lC2, self.location_product_1.corridor)
        self.assertEqual(result.lC3, self.location_product_1.shelf)
        self.assertEqual(result.lC4, self.location_product_1.height)
        self.assertEqual(result.lC5, self.location_product_1.box)
        self.assertEqual(result.lCCD, self.location_product_1.get_checksum())

        self.assertEqual(result.Usf01, self.lot_product_1.voice_identifier)

    def test_requ_location_deleted_packop(self):
        """
        :return:
        """
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()
        pack_op_id = pack_op.id
        pack_op.unlink()
        self.assertFalse(self.picking.is_zetes_error)

        domain = Location(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "lineId": pack_op_id,
                "Cri01": self.location_product_1.zone,
                "Cri02": self.location_product_1.corridor,
                "Cri03": self.location_product_1.shelf,
                "Cri04": self.location_product_1.height,
                "Cri05": self.location_product_1.box,
                "Cri07": self.lot_product_1.checksum,
            }
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))
        self.assertTrue(self.picking.is_zetes_error)
