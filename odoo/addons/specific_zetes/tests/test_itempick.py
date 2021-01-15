# -*- coding: utf-8 -*-
import mock

from .. import constants
from ..tools.domain_interface import Parameters
from ..tools.domain_itempick import Itempick
from .zetes_test_classes import ZetesTest


class TestItempick(ZetesTest):
    def setUp(self):
        self.disable_picking_validation = True
        super(TestItempick, self).setUp()
        self.location_product_2 = self.env["stock.location"].create(
            {
                "name": "GD80B3",
                "kind": "bin",
                "zone": "G",
                "corridor": "D",
                "shelf": "80",
                "height": "B",
                "box": "3",
                "location_id": self.zone_gustave.id,
                "bin_checksum_1": "12",
                "bin_checksum_2": "12",
            }
        )
        self.env["stock.location"]._parent_store_compute()
        # Product 2
        # Location: GD80B3
        self.product_2 = self.env["product.product"].create(
            {
                "name": "Test medoc 2",
                "default_code": "1234568",
                "categ_id": self.product_categ_medoc.id,
                "tracking": "none",
                "list_price": 100,
                "indicated_price": 120,
                "type": "product",
                "stock_bin_ids": [
                    (
                        0,
                        0,
                        {
                            "sequence": 1,
                            "location_id": self.stock_location.id,
                            "bin_location_id": self.location_product_2.id,
                        },
                    )
                ],
            }
        )
        update_qty_wizard_2 = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_2.id,
                "product_tmpl_id": self.product_2.product_tmpl_id.id,
                "new_quantity": 100,
                "location_id": self.location_product_2.id,
            }
        )
        update_qty_wizard_2.change_product_qty()
        self.picking_2 = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.picking_type_medoc.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.env.ref("stock.stock_location_output").id,
                "zetes_state": constants.AS_DEFAULT,
                "move_lines": [
                    (
                        0,
                        0,
                        {
                            "name": "Test medoc 2",
                            "product_id": self.product_2.id,
                            "product_uom_qty": 10,
                            "product_uom": self.env.ref("product.product_uom_unit").id,
                            "picking_type_id": self.picking_type_medoc.id,
                        },
                    )
                ],
            }
        )
        self.picking.action_assign()
        self.picking_2.action_assign()
        # Round to the picking
        self.round.button_update()

    def test_requ_itempick_price(self):
        """
        """

        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))

        # Set the flag is_price_on_labels
        self.partner.write({"is_price_on_labels": True})
        customer = self.partner.copy()
        customer.is_b2c_customer = True
        self.picking.customer_id = customer

        request_params = Parameters(domain, action="requ")
        request_params.update(
            {"groupNum": self.picking.id, "Cri01": None, "Usf06": None}
        )

        # customer has flag is_b2c_customer
        # -> the price must not be set
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertFalse(result.Usf07)
        # unset flag is_b2c_customer on customer
        # -> the price must be set
        customer.is_b2c_customer = False
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertTrue(result.Usf07)
        # unset flag is_price_on_labels on the partner
        # -> the price must not be set
        self.partner.is_price_on_labels = False
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertFalse(result.Usf07)

    def test_requ_itempick(self):
        """
        The method requ on catchweight is not used.
        :return:
        """
        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))

        # Set the flag is_price_on_labels
        self.partner.write({"is_price_on_labels": True})

        request_params = Parameters(domain, action="requ")
        request_params.update(
            {"groupNum": self.picking.id, "Cri01": None, "Usf06": None}
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        pack_op_id, lot_id = result.pickLineId.split("_")

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.groupNum, str(self.picking.id))
        self.assertEqual(pack_op_id, str(pack_op.id))
        self.assertEqual(lot_id, str(lot_id))
        self.assertEqual(result.reqDestCarSeqNum, "1")
        self.assertEqual(int(result.reqQty), 10)
        self.assertEqual(int(result.effQty), 0)
        self.assertEqual(result.pickStatus, str(constants.OP_DEFAULT))
        self.assertEqual(result.tripCounter, "1")
        self.assertEqual(result.productCode, self.product_1.default_code)
        self.assertEqual(result.productDescription, self.product_1.name)
        self.assertFalse(result.productProperty1)
        self.assertEqual(result.productProperty2, "0")
        self.assertEqual(result.lessQtyAllowed, "1")
        self.assertEqual(result.moreQtyAllowed, "0")
        self.assertEqual(result.catchWeightFlag, "0")
        self.assertEqual(result.cycleCountFlag, "0")
        self.assertEqual(result.expiryDateCheckFlag, "0")
        self.assertEqual(result.productBarcode, self.product_1.barcode or "")
        self.assertEqual(result.scanProductBarcode, "0")
        # self.assertEqual(result.UOMPrompt, move.product_uom_id.name)
        self.assertEqual(result.itemPickSeqNum, "1")
        self.assertEqual(float(result.Usf07), 120.0)
        self.assertEqual(result.lotTrackingFlag, "1")

        # Check location
        self.assertEqual(result.sourceLC1, self.location_product_1.zone)
        self.assertEqual(result.sourceLC2, self.location_product_1.corridor)
        self.assertEqual(result.sourceLC3, self.location_product_1.shelf)
        self.assertEqual(result.sourceLC4, self.location_product_1.height)
        self.assertEqual(result.sourceLC5, self.location_product_1.box)
        self.assertEqual(result.sourceLCCD, self.location_product_1.get_checksum())

        # Check lot name
        self.assertEqual(result.Usf01, self.lot_product_1.voice_identifier)

    def test_resu_itempick(self):
        """
        Cancel the move
        :return:
        """
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        pack_op.pack_lot_ids.write({"qty": 10})
        pack_op.write({"qty_done": 10})

        self.assertEqual(pack_op.qty_done, 10)

        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {"pickLineId": pack_op.id, "pickStatus": constants.OP_CANCELED}
        )

        domain.resu(request_params)
        self.assertEqual(pack_op.zetes_state, constants.OP_CANCELED)
        self.assertEqual(pack_op.qty_done, 0)
        self.assertEqual(len(pack_op.pack_lot_ids), 1)

    def test_resu_itempick_deleted_packop(self):
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()
        pack_op_id = pack_op.id
        pack_op.unlink()
        self.assertFalse(self.picking.is_zetes_error)
        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="resu")
        request_params.update(
            {"pickLineId": pack_op_id, "pickStatus": constants.OP_CANCELED}
        )
        domain.resu(request_params)
        self.assertTrue(self.picking.is_zetes_error)

    def test_requ_itempick_lot_shortage(self):
        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking.id,
                "Cri01": None,
                "Usf06": constants.OP_CUT,
                "Usf02": "%s_%s"
                % (self.picking.pack_operation_product_ids.id, self.lot_product_1.id),
                "Usf04": "0",
            }
        )
        # As the original picking has a different src location as the operation
        # we keep the original src location of the operation
        stock_op_location = self.picking.pack_operation_product_ids.location_id
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_NO_LINES))
        self.assertFalse(result.respMsg)
        new_operation = self.env["stock.pack.operation"].search(
            [("product_id", "=", self.product_1.id)]
        )
        # Although the qty on the picking was 10.0, the new operation must
        # empty the existing qty on the picking location
        self.assertEqual(new_operation.product_qty, 100.0)
        new_picking = new_operation.picking_id
        self.assertNotEqual(new_picking, self.picking)
        # Check that new operation has the same src location as before
        self.assertEqual(new_operation.location_id, stock_op_location)
        # Check that new operation has loss location as destination
        self.assertEqual(
            new_operation.location_dest_id,
            self.env.ref("stock_lot_loss.stock_location_14019"),
        )

    def test_requ_itempick_lot_shortage_deleted_packop(self):
        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()
        pack_op_id = pack_op.id
        pack_op.unlink()
        self.assertFalse(self.picking.is_zetes_error)
        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking.id,
                "Cri01": None,
                "Usf06": constants.OP_CUT,
                "Usf02": "{}_{}".format(pack_op_id, self.lot_product_1.id),
                "Usf04": "0",
            }
        )
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))
        self.assertTrue(self.picking.is_zetes_error)

    def test_requ_itempick_no_tracking_shortage(self):
        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking_2.id,
                "Cri01": None,
                "Usf06": constants.OP_CUT,
                "Usf02": str(self.picking_2.pack_operation_product_ids.id),
                "Usf04": "0",
            }
        )
        # As the original picking has a different src location as the operation
        # we keep the original src location of the operation
        stock_op_location = self.picking_2.pack_operation_product_ids.location_id
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_NO_LINES))
        self.assertFalse(result.respMsg)
        new_operation = self.env["stock.pack.operation"].search(
            [("product_id", "=", self.product_2.id)]
        )
        # Although the qty on the picking was 10.0, the new operation must
        # empty the existing qty on the picking location
        self.assertEqual(new_operation.product_qty, 100.0)
        new_picking = new_operation.picking_id
        self.assertNotEqual(new_picking, self.picking_2)
        # Check that new operation has the same src location as before
        self.assertEqual(new_operation.location_id, stock_op_location)
        # Check that new operation has loss location as destination
        self.assertEqual(
            new_operation.location_dest_id,
            self.env.ref("stock_lot_loss.stock_location_14019"),
        )

    def test_requ_itempick_no_tracking_false_shortage(self):
        # Here we declare a shortage but the request contains all the qty to pick
        # in this case the code should not fails
        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking_2.id,
                "Cri01": None,
                "Usf06": constants.OP_CUT,
                "Usf02": str(self.picking_2.pack_operation_product_ids.id),
                "Usf04": "%d" % self.picking_2.pack_operation_product_ids.product_qty,
            }
        )
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)
        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_NO_LINES))
        self.assertFalse(result.respMsg)

    def test_requ_itempick_zero_check(self):
        """
        Test the ZeroCheck flag
        :return:
        """
        domain = Itempick(self._default_header(), mock.MagicMock(name="Savepoint()"))

        request_params = Parameters(domain, action="requ")
        request_params.update(
            {"groupNum": self.picking.id, "Cri01": None, "Usf06": None}
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        self.assertEqual(result.cycleCountFlag, "0")

        # Empty the stock
        update_qty_wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": self.product_1.id,
                "product_tmpl_id": self.product_1.product_tmpl_id.id,
                "new_quantity": 10,
                "lot_id": self.lot_product_1.id,
                "location_id": self.location_product_1.id,
            }
        )
        update_qty_wizard.change_product_qty()

        request_params = Parameters(domain, action="requ")
        request_params.update(
            {"groupNum": self.picking.id, "Cri01": None, "Usf06": None}
        )

        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_OK))
        # FIXME: Zero Check has been disabled
        # self.assertEqual(result.cycleCountFlag, '1')
