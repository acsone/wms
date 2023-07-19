# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class CommonTestStockReceptionRankCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        # we create a product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "type": "product",
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product2",
                "type": "product",
            }
        )
        # we create a partner to use as a supplier
        cls.supplier = cls.env["res.partner"].create(
            {
                "name": "Supplier",
            }
        )
        # create 2 cutomers
        cls.customer1 = cls.env["res.partner"].create(
            {
                "name": "Customer1",
            }
        )
        cls.customer2 = cls.env["res.partner"].create(
            {
                "name": "Customer2",
            }
        )
        # we create an incoming picking for the product
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.receipt_type = cls.env.ref("stock.picking_type_in")
        cls.delivery_type = cls.env.ref("stock.picking_type_out")
        cls.incoming_picking = cls.env["stock.picking"].create(
            {
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "picking_type_id": cls.receipt_type.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "test_rank",
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1.0,
                "picking_id": cls.incoming_picking.id,
                "picking_type_id": cls.receipt_type.id,
            }
        )
        # we confirm the incoming picking
        cls.incoming_picking.action_confirm()

        # we create a second incoming picking for 2 products
        cls.incoming_picking_2_products = cls.env["stock.picking"].create(
            {
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "picking_type_id": cls.receipt_type.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "test_rank",
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "product_id": cls.product.id,
                "product_uom": cls.product.uom_id.id,
                "product_uom_qty": 1.0,
                "picking_id": cls.incoming_picking_2_products.id,
                "picking_type_id": cls.receipt_type.id,
            }
        )
        cls.env["stock.move"].create(
            {
                "name": "test_rank",
                "location_id": cls.supplier_location.id,
                "location_dest_id": cls.stock_location.id,
                "product_id": cls.product2.id,
                "product_uom": cls.product2.uom_id.id,
                "product_uom_qty": 1.0,
                "picking_id": cls.incoming_picking_2_products.id,
                "picking_type_id": cls.receipt_type.id,
            }
        )
        cls.incoming_picking_2_products.action_confirm()
        cls.env["stock.release.channel"].search([]).write({"active": False})
        # we create a release_channel
        cls.release_channel = cls.env["stock.release.channel"].create(
            {
                "name": "Test",
            }
        )

        cls.env.flush_all()

    def _create_outgoing_picking(self, partner, qty=1, product=None):
        """Create an outgoing picking for the product."""
        product = product or self.product
        outgoing_picking = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.delivery_type.id,
                "partner_id": partner.id,
            }
        )
        self.env["stock.move"].create(
            {
                "name": "test_rank",
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "product_uom_qty": qty,
                "picking_id": outgoing_picking.id,
                "picking_type_id": self.delivery_type.id,
                "partner_id": partner.id,
            }
        )
        outgoing_picking.action_confirm()
        outgoing_picking.action_assign()
        self.env.flush_all()
        return outgoing_picking

    def assert_no_waiting(self, picking=None):
        picking = picking or self.incoming_picking
        self.assertEqual(picking.count_partners_waiting_for_reception, 0)
        self.assertEqual(picking.count_products_waiting_for_reception, 0)
