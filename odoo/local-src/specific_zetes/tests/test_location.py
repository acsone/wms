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
        move = self.picking.pack_operation_product_ids
        move.ensure_one()

        domain = Location(DEFAULT_HEADER, request_overwrite=self)
        request_params = Parameters(domain, action='requ')
        request_params.update({
            'lineId': move.id,
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
        location = self.env.ref('__import__.location_loc_GAA210')
        self.assertEqual(result.lC1, location.zone)
        self.assertEqual(result.lC2, location.corridor)
        self.assertEqual(result.lC3, location.shelf)
        self.assertEqual(result.lC4, location.height)
        self.assertEqual(result.lC5, location.box)
        self.assertEqual(result.lCCD, location.get_checksum())

        self.assertEqual(result.Usf01, self.lot_product_1.checksum)
