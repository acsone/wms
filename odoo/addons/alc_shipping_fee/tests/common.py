# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestShippingFeeCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create the product used for "shipping alcyon fees" and is xmlid
        cls.product_shipping_cost = cls.env["product.product"].create(
            {"name": "Alcyon shipping cost test"}
        )
        # Create the delivery carrier for Alcyon
        cls.fee = 8.5
        carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.delivery_method = cls.env["delivery.carrier"].create(
            {
                "delivery_type": "fixed",
                "fixed_price": cls.fee,
                "free_over": True,
                "amount": 125,
                "use_specific_cost_calculation": True,
                "name": "Alcyon",
                "product_id": carrier_product.id,
            }
        )
        cls.fee_2 = 20
        carrier_product_2 = cls.env["product.product"].create(
            {
                "name": "Test carrier product 2",
                "type": "service",
            }
        )
        cls.delivery_method_2 = cls.env["delivery.carrier"].create(
            {
                "delivery_type": "fixed",
                "fixed_price": cls.fee_2,
                "free_over": True,
                "amount": 200,
                "use_specific_cost_calculation": True,
                "name": "Alcyon 2",
                "product_id": carrier_product_2.id,
            }
        )

        cls.fee_3 = 25
        carrier_product_3 = cls.env["product.product"].create(
            {
                "name": "Test carrier product 3",
                "type": "service",
            }
        )
        cls.delivery_method_3 = cls.env["delivery.carrier"].create(
            {
                "delivery_type": "fixed",
                "fixed_price": cls.fee_3,
                "free_over": True,
                "amount": 200,
                "use_specific_cost_calculation": False,
                "name": "Alcyon 3",
                "product_id": carrier_product_3.id,
            }
        )

        cls.fixed_fee = 2
        carrier_product_4 = cls.env["product.product"].create(
            {
                "name": "Test carrier product 4",
                "type": "service",
            }
        )
        cls.delivery_method_4 = cls.env["delivery.carrier"].create(
            {
                "delivery_type": "fixed",
                "use_specific_cost_calculation": True,
                "fixed_price": 0,
                "fixed_fee_for_delivery": cls.fixed_fee,
                "name": "Alcyon fixed fee",
                "product_id": carrier_product_4.id,
            }
        )
        carrier_product_5 = cls.env["product.product"].create(
            {
                "name": "Test carrier product 5",
                "type": "service",
            }
        )
        cls.delivery_method_5 = cls.env["delivery.carrier"].create(
            {
                "delivery_type": "fixed",
                "use_specific_cost_calculation": True,
                "fixed_price": cls.fee,
                "free_over": True,
                "amount": 150,
                "fixed_fee_for_delivery": cls.fixed_fee,
                "name": "Alcyon fixed and extra fee",
                "product_id": carrier_product_5.id,
            }
        )

        # Lets create 3 customers
        cls.partner1 = cls.env["res.partner"].create(
            {"name": "Partner One", "ref": "89328492342", "help_with_fee": True}
        )
        cls.partner2 = cls.env["res.partner"].create(
            {"name": "Partner Two", "ref": "498298349283", "help_with_fee": True}
        )
        cls.partner3 = cls.env["res.partner"].create(
            {
                "name": "Partner 3",
                "ref": "89328492111",
                "help_with_fee": True,
                "help_with_fixed_fee": True,
            }
        )

        # Create a couple of products
        cls.p1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        cls.p3 = cls.env["product.product"].create(
            {
                "name": "P3",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "type": "product",
            }
        )
        # Add some stock for p1 and p2
        cls._create_inventory(cls.p1, 100)
        cls._create_inventory(cls.p2, 100)
        # Create a sale order 1 for partner 1
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner1.id,
                "carrier_id": cls.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        # Create sale order 2 for partner 1
        cls.so2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner1.id,
                "carrier_id": cls.delivery_method.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.p1.name,
                            "product_id": cls.p1.id,
                            "product_uom": cls.env.ref("uom.product_uom_unit").id,
                            "product_uom_qty": 1,
                            "price_unit": 10,
                        },
                    )
                ],
            }
        )
        # Create a release_channel
        cls.rc1 = cls.env["stock.release.channel"].create(
            {"name": "release channel 1", "state": "open"}
        )

    @classmethod
    def _create_inventory(cls, product, qty):
        inventory_quant = cls.env["stock.quant"].create(
            {
                "location_id": cls.env.ref("stock.stock_location_stock").id,
                "product_id": product.id,
                "inventory_quantity": qty,
            }
        )
        inventory_quant.action_apply_inventory()

    def get_shipping_cost(self, so):
        """Returns the amount of shipping cost billed on a sale order."""
        delivery_line = so.order_line.filtered("is_delivery")
        return sum(delivery_line.mapped("price_unit"))

    def product_used_for_cost_so_line(self, so):
        """Returns the product id used on the sale order line with thefee."""
        delivery_line = so.order_line.filtered("is_delivery")
        return delivery_line.product_id

    def no_shipping_line_present(self, so):
        delivery_line = so.order_line.filtered("is_delivery")
        return not bool(len(delivery_line))

    @staticmethod
    def do_picking(picking):
        picking.action_set_quantities_to_reservation()
        picking.button_validate()
