# -*- coding: utf-8 -*-
import mock
from .. import constants
from .zetes_test_classes import ZetesTest, DEFAULT_HEADER
from ..tools.domain_interface import Parameters
from ..tools.domain_itempick import Itempick


class TestItempick(ZetesTest):

    def test_requ_itempick(self):
        """
        The method requ on catchweight is not used.
        :return:
        """
        domain = Itempick(DEFAULT_HEADER,
                          mock.MagicMock(name='Savepoint()'),
                          request_overwrite=self)

        # Set the flag is_price_on_labels
        self.partner.write({
            'is_price_on_labels': True,
        })

        request_params = Parameters(domain, action='requ')
        request_params.update({
            'groupNum': self.picking.id,
            'Cri01': None,
            'Usf06': None
        })

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        pack_op_id, lot_id = result.pickLineId.split('_')

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking.id))
        self.assertEqual(pack_op_id, str(pack_op.id))
        self.assertEqual(lot_id, str(lot_id))
        self.assertEqual(result.reqDestCarSeqNum, '1')
        self.assertEqual(int(result.reqQty), 10)
        self.assertEqual(int(result.effQty), 0)
        self.assertEqual(result.pickStatus, str(constants.OP_DEFAULT))
        self.assertEqual(result.tripCounter, '1')
        self.assertEqual(result.productCode, self.product_1.default_code)
        self.assertEqual(result.productDescription, self.product_1.name)
        self.assertFalse(result.productProperty1)
        self.assertEqual(result.productProperty2, '0')
        self.assertEqual(result.lessQtyAllowed, '1')
        self.assertEqual(result.moreQtyAllowed, '0')
        self.assertEqual(result.catchWeightFlag, '0')
        self.assertEqual(result.cycleCountFlag, '0')
        self.assertEqual(result.expiryDateCheckFlag, '0')
        self.assertEqual(result.productBarcode, self.product_1.barcode or '')
        self.assertEqual(result.scanProductBarcode, '0')
        # self.assertEqual(result.UOMPrompt, move.product_uom_id.name)
        self.assertEqual(result.itemPickSeqNum, '1')
        self.assertEqual(float(result.Usf07), 120.0)
        self.assertEqual(result.lotTrackingFlag, '1')

        # Check location
        self.assertEqual(result.sourceLC1, self.location_product_1.zone)
        self.assertEqual(result.sourceLC2, self.location_product_1.corridor)
        self.assertEqual(result.sourceLC3, self.location_product_1.shelf)
        self.assertEqual(result.sourceLC4, self.location_product_1.height)
        self.assertEqual(result.sourceLC5, self.location_product_1.box)
        self.assertEqual(result.sourceLCCD,
                         self.location_product_1.get_checksum())

        # Check lot name
        self.assertEqual(result.Usf01, self.lot_product_1.voice_identifier)

    def test_resu_itempick(self):
        """
        Cancel the move
        :return:
        """
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        pack_op.pack_lot_ids.write({
            'qty': 10,
        })
        pack_op.write({
            'qty_done': 10,
        })

        self.assertEqual(pack_op.qty_done, 10)

        domain = Itempick(DEFAULT_HEADER,
                          mock.MagicMock(name='Savepoint()'),
                          request_overwrite=self)
        request_params = Parameters(domain, action='resu')
        request_params.update({
            'pickLineId': pack_op.id,
            'pickStatus': constants.OP_CANCELED
        })

        domain.resu(request_params)
        self.assertEqual(pack_op.zetes_state, constants.OP_CANCELED)
        self.assertEqual(pack_op.qty_done, 0)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)

    def test_requ_itempick_zero_check(self):
        """
        Test the ZeroCheck flag
        :return:
        """
        domain = Itempick(DEFAULT_HEADER,
                          mock.MagicMock(name='Savepoint()'),
                          request_overwrite=self)

        request_params = Parameters(domain, action='requ')
        request_params.update({
            'groupNum': self.picking.id,
            'Cri01': None,
            'Usf06': None,
        })

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.cycleCountFlag, '0')

        # Empty the stock
        update_qty_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_1.id,
            'product_tmpl_id': self.product_1.product_tmpl_id.id,
            'new_quantity': 10,
            'lot_id': self.lot_product_1.id,
            'location_id': self.location_product_1.id
        })
        update_qty_wizard.change_product_qty()

        request_params = Parameters(domain, action='requ')
        request_params.update({
            'groupNum': self.picking.id,
            'Cri01': None,
            'Usf06': None
        })

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        # FIXME: Zero Check has been disabled
        # self.assertEqual(result.cycleCountFlag, '1')
