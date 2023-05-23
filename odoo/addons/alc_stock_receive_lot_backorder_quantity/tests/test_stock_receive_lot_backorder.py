# Copyright 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase

from odoo.addons.alc_stock_receive_lot.tests.common import PackOperationLotAddCommon


class TestPackOperationLotAddBackorder(PackOperationLotAddCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create a picking out for customer
        product = cls.picking.move_ids[0].move_line_ids[0].product_id
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.move_out = cls.env["stock.move"].create(
            {
                "name": "Test out",
                "product_id": product.id,
                "location_id": cls.stock_location.id,
                "location_dest_id": cls.env.ref("stock.stock_location_customers").id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": 4.0,
                "picking_type_id": cls.picking_type_out.id,
            }
        )

    def test_receive(self):
        self.move_out._action_confirm()
        self.move_out._action_assign()
        picking = self.picking
        product = picking.move_ids[0].move_line_ids[0].product_id
        wizard = self.env["stock.change.product.qty"].create(
            {
                "product_id": product.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "new_quantity": 0.0,
            }
        )
        wizard.change_product_qty()

        # launch wizard
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).new({"picking_id": picking.id})

        op1 = picking.move_ids[0].move_line_ids[0]

        # select operation
        wiz.move_line_id = op1
        self.assertEqual(5, wiz.remaining_qty)

        self.assertEqual(4.0, wiz.qty_backorder)

        # select destination
        wiz.location_dest_id = self.bin1.id

        wiz.lot_name = "Unittest Reception L1"
        wiz.expiration_date = "2030-01-01 10:00:00"
        wiz.qty = 3

        res = wiz.button_transfer()

        self.assertTrue(isinstance(res, dict))

        backorder_wizard = (
            self.env[res["res_model"]].with_context(**res["context"]).create({})
        )
        backorder_wizard.process()

        picking = self.env["stock.picking"].search([("backorder_id", "=", picking.id)])
        wiz = self.stock_reception_wizard.with_context(
            default_expiration_date_allowed=True
        ).new({"picking_id": picking.id})

        op1 = picking.move_ids.filtered(
            lambda m: m.product_id == product
        ).move_line_ids[0]

        op1.product_id.invalidate_recordset()

        # select operation
        wiz.move_line_id = op1

        self.assertEqual(1.0, wiz.qty_backorder)
