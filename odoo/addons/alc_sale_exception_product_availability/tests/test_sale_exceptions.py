# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.alc_sale_exception_settings.tests.common import (
    TestSaleOrderExceptionCommon,
)


class TestSaleOrderException(TestSaleOrderExceptionCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.current_module = "alc_sale_exception_product_availability"
        cls.current_exception_ids = cls.get_module_exception_ids()
        cls.activate_module_exceptions_only()

        cls.prod2 = cls.env["product.product"].create(
            {
                "name": "I am a Prod 2",
            }
        )
        cls.prod_provision_on_sale = cls.env["product.product"].create(
            {
                "name": "product provision on sale",
            }
        )
        route = cls.env.ref("stock.route_warehouse0_mto")
        route.active = True
        cls.prod_provision_on_sale.route_ids = route
        cls.so1_vals.update(
            {
                "client_order_ref": "whatever the client want",
            }
        )
        cls.so1 = cls.env["sale.order"].create(cls.so1_vals)
        cls.prod1.type = "product"

    def test_exception_warning_provision_on_order(self):
        """Check the warning provision on order."""
        exception = self.env.ref(
            "alc_sale_exception_product_availability.provision_on_order"
        )
        exception.active = True
        line = self.so1.order_line[0]
        line.product_id = self.prod_provision_on_sale
        self.assertIn(exception.description, line.warning_text)

    def test_no_backorder_rule(self):
        """Check the no backorder rule.

        A customer can be configured to not accept a sale order which implies
        some back order.
        """
        no_backorder_rule = self.env.ref(
            "alc_sale_exception_product_availability.no_backorder"
        )
        no_backorder_rule.active = True
        self.partner.sale_reason_backorder_strategy = "cancel"
        line = self.so1.order_line[0]
        line.product_uom_qty = 234
        self.assertEqual(no_backorder_rule.description, line.exception)
        # If quantity ordered is zero exception should not be raised (not active)
        line.product_uom_qty = 0
        self.assertEqual("", line.exception)
        # And if it is set to a positive number raised again
        line.product_uom_qty = 234
        self.assertEqual(no_backorder_rule.description, line.exception)
        # Check customer accept back order
        self.partner.sale_reason_backorder_strategy = "create"
        line.product_uom_qty = 534
        self.assertEqual("", line.exception)

    def test_exception_out_of_stock_at_supplier(self):
        """Check warning for out of stock at supplier level."""
        exception = self.env.ref(
            "alc_sale_exception_product_availability.warning_supplier_break"
        )
        exception.active = True
        line = self.so1.order_line[0]
        # Set the Out Of Stock At Supplier Level state on the product
        # And switch the product to trigger the exceptions
        self.prod1.product_state_id = self.env.ref("alc_product_state.product_state_h")
        line.product_id = self.prod2
        line.product_id = self.prod1
        self.assertIn(exception.description, line.warning_text)
        # With some inventory there should be no warning
        stock_location = self.env.ref("stock.stock_location_stock")
        quant = self.env["stock.quant"].create(
            {
                "product_id": self.prod1.product_variant_id.id,
                "inventory_quantity": 1000,
                "location_id": stock_location.id,
            }
        )
        quant.action_apply_inventory()
        # Cache refreshing needed for the back order calculation to work ?
        self.prod1.invalidate_recordset()
        line.product_id = self.prod2
        line.product_id = self.prod1
        self.assertNotIn(exception.description, str(line.warning_text))
