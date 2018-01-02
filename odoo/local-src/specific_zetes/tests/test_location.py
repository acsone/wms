# -*- coding: utf-8 -*-
from .. import constants
from .zetes_test_classes import ZetesTest, DEFAULT_HEADER
from ..tools.domain_interface import Parameters
from ..tools.domain_location import Location


class TestLocation(ZetesTest):

    def test_requ_location(self):
        """
        :return:
        """
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        domain = Location(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'lineId': pack_op.id,
            'Cri01': self.location_product_1.zone,
            'Cri02': self.location_product_1.corridor,
            'Cri03': self.location_product_1.shelf,
            'Cri04': self.location_product_1.height,
            'Cri05': self.location_product_1.box,
            'Cri07': None,
        })

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.productCode, self.product_1.default_code)
        self.assertEqual(result.productDescription, self.product_1.name)
        self.assertEqual(result.quantity, '100.0')
        self.assertEqual(result.Usf07, '100.0')

        # Check location
        self.assertEqual(result.lC1, self.location_product_1.zone)
        self.assertEqual(result.lC2, self.location_product_1.corridor)
        self.assertEqual(result.lC3, self.location_product_1.shelf)
        self.assertEqual(result.lC4, self.location_product_1.height)
        self.assertEqual(result.lC5, self.location_product_1.box)
        self.assertEqual(result.lCCD, self.location_product_1.get_checksum())

        self.assertEqual(result.Usf01, self.lot_product_1.checksum)
