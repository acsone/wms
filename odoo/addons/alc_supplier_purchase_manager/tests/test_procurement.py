# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.purchase_stock.tests.common import TestStockCommon


class TestProcurement(TestStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.purchase_manager_user = cls.env.ref("base.user_demo")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        # route buy should be there by default
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Jhon",
                "purchase_manager_id": cls.purchase_manager_user.id,
            }
        )

        cls.product = cls.env["product.product"].create(
            {
                "name": "product",
                "type": "product",
                "route_ids": [
                    (4, cls.env.ref("stock.route_warehouse0_mto").id),
                    (4, cls.env.ref("purchase_stock.route_warehouse0_buy").id),
                ],
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.partner.id,
                            "price": 12.0,
                            "delay": 7,
                        },
                    )
                ],
                "categ_id": cls.env.ref("product.product_category_all").id,
            }
        )

        cls.seller = cls.product.seller_ids[0]

        # declare minimal stock rule
        order_point = cls.env["stock.warehouse.orderpoint"].create(
            {
                "name": "Test rule",
                "location_id": cls.stock_location.id,
                "product_id": cls.product.id,
                "product_min_qty": 10,
                "product_max_qty": 20,
                "product_uom": cls.product.uom_id.id,
                "warehouse_id": cls.warehouse.id,
                "supplier_id": cls.seller.id,
            }
        )
        cls.order_point = order_point
        cls.customer_1 = cls.env["res.partner"].create(
            {
                "name": "Customer 1",
            }
        )
        cls.customer_2 = cls.env["res.partner"].create(
            {
                "name": "Customer 2",
            }
        )

    def test_same_po(self):
        # create a picking out for the product and customer 1
        picking_1 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.customer_1.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "move",
                            "product_id": self.product.id,
                            "product_uom_qty": 10,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                            "picking_type_id": self.picking_type_out.id,
                            "procure_method": "make_to_stock",
                        },
                    )
                ],
            }
        )
        # confirm the picking
        picking_1.action_confirm()
        # check that a PO has been created
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product.id)]
        )
        self.assertTrue(po_line)
        po = po_line.order_id
        self.assertEqual(po.user_id, self.purchase_manager_user)

        # create a picking out for the product and customer 1
        picking_2 = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_out.id,
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "partner_id": self.customer_2.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "move",
                            "product_id": self.product.id,
                            "product_uom_qty": 30,
                            "product_uom": self.product.uom_id.id,
                            "location_id": self.stock_location.id,
                            "location_dest_id": self.customer_location.id,
                            "picking_type_id": self.picking_type_out.id,
                            "procure_method": "make_to_stock",
                        },
                    )
                ],
            }
        )
        # confirm the picking
        picking_2.action_confirm()
        # check that the same PO has been used
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.product.id)]
        )
        new_po = po_line.order_id
        self.assertEqual(po.id, new_po.id)
        # and we only have 1 line
        self.assertEqual(1, len(po_line))
        # and the qty is 40
        self.assertEqual(
            self.order_point.product_max_qty
            + picking_1.move_ids.product_uom_qty
            + picking_2.move_ids.product_uom_qty,
            po_line.product_qty,
        )
