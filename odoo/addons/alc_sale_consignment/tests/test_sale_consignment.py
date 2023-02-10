# Copyright 2020 CamptocampSavepointCase
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged("-at_install", "post_install")
class TestSaleconsignment(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env.ref("base.res_partner_12")
        cls.partner.ref = 1
        cls.product = cls.env["product.product"].create(
            {"name": "Product 1", "list_price": 11.0}
        )

        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 7,
                        },
                    )
                ],
            }
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")

    def _return_pick(self, picking, returned_qty):
        stock_return_picking_form = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=picking.ids,
                active_id=picking.id,
                active_model="stock.picking",
            )
        )
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = returned_qty
        action = stock_return_picking.create_returns()
        return_pick = self.env["stock.picking"].browse(action["res_id"])
        return_pick.move_ids.quantity_done = returned_qty
        return_pick._action_done()
        return return_pick

    def test_sale_not_consignment(self):
        self.so.action_confirm()
        picking = self.so.picking_ids
        self.assertEqual(picking.location_dest_id, self.customer_location)
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.move_line_ids.qty_done = 7.0
        picking._action_done()
        sol = self.so.order_line
        self.assertEqual(sol.qty_delivered, 7.0)
        self._return_pick(picking, 2)
        self.assertEqual(sol.qty_delivered, 5.0)
        self.assertEqual(sol.qty_invoiced, 0.0)

    def test_sale_is_consignment(self):
        self.so.is_consignment = True
        self.so.action_confirm()
        sol = self.so.order_line
        picking = self.so.picking_ids
        self.assertNotEqual(picking.location_dest_id, self.customer_location)
        self.assertEqual(
            picking.location_dest_id, self.partner.property_stock_consignment_customer
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_ids.move_line_ids.qty_done = 7.0
        picking._action_done()
        self.assertEqual(sol.qty_delivered, 0.0)
        self._return_pick(picking, 2)
        self.assertEqual(sol.qty_delivered, 0.0)
