# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class StockPickingTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
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
        cls.loc_stock = cls.warehouse_1.lot_stock_id
        # Create additional product and update the available quantity (15)
        cls.additional_product = cls.env["product.product"].create(
            {
                "name": "Additional product",
                "default_code": "987654321",
                "tracking": "none",
                "list_price": 20,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.additional_product, cls.loc_stock, 500.0
        )

        # Create main product linked to the additional product with quanity 20

        cls.main_product = cls.env["product.product"].create(
            {
                "name": "Test medoc 1",
                "default_code": "1234567",
                "tracking": "none",
                "list_price": 100,
                "type": "product",
                "additional_product_id": cls.additional_product.id,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "ratio_main_product": 1,
                "ratio_additional_product": 5,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.main_product, cls.loc_stock, 100.0
        )

        cls.main_product2 = cls.env["product.product"].create(
            {
                "name": "Main product2",
                "default_code": "1234567",
                "tracking": "none",
                "list_price": 100,
                "type": "product",
                "additional_product_id": cls.additional_product.id,
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "ratio_main_product": 1,
                "ratio_additional_product": 5,
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.main_product2, cls.loc_stock, 100.0
        )

        # Create a product without promotion
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "default_code": "984928374",
                "tracking": "lot",
                "list_price": 100,
                "type": "product",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_2, cls.loc_stock, 100.0
        )
        cls.product_3 = cls.env["product.product"].create(
            {
                "name": "Product 3",
                "default_code": "984928375",
                "tracking": "lot",
                "list_price": 100,
                "type": "product",
            }
        )
        cls.env["stock.quant"]._update_available_quantity(
            cls.product_3, cls.loc_stock, 100.0
        )
        cls.pick_type = cls.warehouse_1.out_type_id
        cls.pick_type.search([]).write(
            {"allow_additional_product_on_reserved_qty": True}
        )

    @classmethod
    def _confirm_sale_order(cls, partner=None, products=None, qty=1, carrier_id=None):
        if partner is None:
            partner = cls.partner1
        if products is None:
            lines = [
                Command.create(
                    {
                        "name": cls.main_product.name,
                        "product_id": cls.main_product.id,
                        "product_uom_qty": qty,
                        "product_uom": cls.main_product.uom_id.id,
                        "price_unit": 1,
                    },
                )
            ]
        else:
            lines = [
                Command.create(
                    {
                        "name": product.name,
                        "product_id": product.id,
                        "product_uom_qty": qty,
                        "product_uom": product.uom_id.id,
                        "price_unit": 1,
                    },
                )
                for product in products
            ]
        warehouse = cls.warehouse_1
        Sale = cls.env["sale.order"]

        so_values = {
            "partner_id": partner.id,
            "warehouse_id": warehouse.id,
            "order_line": lines,
        }
        if carrier_id:
            so_values["carrier_id"] = carrier_id
        so = Sale.create(so_values)
        so.action_confirm()
        return so

    def _get_picking_pick(self, so):
        return so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_id.code == "internal"
        )

    def _get_picking_ship(self, so):
        return so.mapped("picking_ids").filtered(
            lambda p: p.picking_type_id.code == "outgoing"
        )

    def _get_additional_move(self, picking):
        return picking.move_ids.filtered(
            lambda m, product=self.additional_product: m.product_id == product
            and m.is_additional_move
            and m.state not in ("done", "cancel")
        )

    def _check_move_assigned(self, move, qty):
        self.assertEqual(move.state, "assigned")
        self.assertEqual(move.product_qty, qty)
        self.assertEqual(move.reserved_availability, qty)
        self.assertTrue(move.move_line_ids)
