# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase


class TestStockMove(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestStockMove, cls).setUpClass()

        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Unittest first partner", "ref": "12344566777878"}
        )

        cls.warehouse_1 = cls.env.ref("stock.warehouse0")
        cls.warehouse_1.write(
            {
                "name": "Test Warehouse",
                "reception_steps": "one_step",
                "delivery_steps": "pick_ship",
                "code": "TST",
            }
        )
        cls.warehouse_1.pick_type_id.subcode = "PICK"
        cls.warehouse_1.pick_type_id.groupbypartner = False
        cls.warehouse_1.out_type_id.groupbypartner = True

        # Create additional product and update the available quantity (15)
        cls.additional_product = cls.env["product.product"].create(
            {
                "name": "Additional product",
                "default_code": "987654321",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
            }
        )

        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.additional_product.id,
                "product_tmpl_id": cls.additional_product.product_tmpl_id.id,
                "new_quantity": 15,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )
        update_qty_wizard.change_product_qty()

        # Create main product linked to the additional product with quanity 20

        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Test medoc 1",
                "default_code": "1234567",
                "tracking": "none",
                "list_price": 100,
                "type": "product",
                "additional_product_id": cls.additional_product.id,
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "ratio_main_product": 1,
                "ratio_additional_product": 1,
            }
        )

        update_qty_wizard = cls.env["stock.change.product.qty"].create(
            {
                "product_id": cls.main_product.id,
                "product_tmpl_id": cls.main_product.product_tmpl_id.id,
                "new_quantity": 100,
                "location_id": cls.warehouse_1.lot_stock_id.id,
            }
        )
        update_qty_wizard.change_product_qty()
        Sale = cls.env["sale.order"]
        so_values = {
            "partner_id": cls.partner1.id,
            "order_line": [
                (
                    0,
                    0,
                    {
                        "name": cls.main_product.name,
                        "product_id": cls.main_product.id,
                        "product_uom_qty": 10,
                        "product_uom": cls.main_product.uom_id.id,
                        "price_unit": 1,
                    },
                )
            ],
        }
        cls.so = Sale.create(so_values)
        cls.so.action_confirm()

    def test_00(self):

        # check the pickings
        pick = self.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_subcode == "PICK"
        )

        ship = self.so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_code == "outgoing"
        )

        pick.action_confirm()
        pick.action_assign()

        for pack in pick.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        pick.do_transfer()

        # Make sure additional product is in the loop
        self.assertIn(self.additional_product, pick.mapped("move_lines.product_id"))
        self.assertIn(
            self.additional_product, pick.mapped("pack_operation_ids.product_id")
        )

        ship.action_confirm()
        ship.action_assign()

        for pack in ship.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        ship.do_transfer()

        # Make sure additional product is in the loop
        self.assertIn(self.additional_product, ship.mapped("move_lines.product_id"))

        sol = self.so.order_line[0]

        # Create return
        wizard = (
            self.env["stock.return.picking"]
            .with_context(active_ids=ship.ids, active_id=ship.id)
            .create({})
        )

        res = wizard.create_returns()
        wizard.product_return_moves[0].to_refund_so = True
        return_pick = ship.browse(res["res_id"])
        return_pick.force_assign()
        return_pick.action_assign()

        for pack in return_pick.pack_operation_product_ids:
            pack.qty_done = pack.product_qty
        return_pick.do_transfer()

        # Make sure only the 10 items from the main product are returned
        self.assertEqual(sol.product_qty_returned, 10.0)
