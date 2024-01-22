# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import Command
from odoo.exceptions import UserError
from odoo.tests.common import Form, TransactionCase


class TestStockSchedulerFilter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_25")
        cls.product2 = cls.env.ref("product.product_product_6")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.supplier = cls.env.ref("base.res_partner_1")
        cls.supplier2 = cls.env.ref("base.res_partner_4")
        cls.warehouse = cls.env.ref("stock.warehouse0")
        buy_route = cls.warehouse.buy_pull_id.route_id
        cls.product.route_ids = buy_route
        cls.product2.route_ids = buy_route
        cls.product_seller = cls.env.ref("product.product_supplierinfo_16")
        cls.product_virtual_available = cls.product.with_context(
            warehouse=cls.warehouse.id
        ).virtual_available
        cls.product_2_virtual_available = cls.product2.with_context(
            warehouse=cls.warehouse.id
        ).virtual_available
        cls.env["ir.config_parameter"].set_param(
            "alc_stock_scheduler_filter.apply_filter_on_orderpoint_scheduler",
            True,
        )

    def _create_delivery_move(self, product, qty):
        ship = self.env["stock.picking"].create(
            {
                "location_id": self.stock_location.id,
                "location_dest_id": self.customer_location.id,
                "picking_type_id": self.ref("stock.picking_type_out"),
                "move_ids": [
                    Command.create(
                        {
                            "name": "Delivery move",
                            "product_id": product.id,
                            "product_uom_qty": qty,
                            "product_uom": product.uom_id.id,
                            "location_id": self.warehouse.lot_stock_id.id,
                            "location_dest_id": self.customer_location.id,
                            "picking_type_id": self.warehouse.in_type_id.id,
                        }
                    )
                ],
            }
        )
        ship.action_confirm()
        return ship

    def _create_orderpoint(self, product, seller):
        self.env["stock.warehouse.orderpoint"].create(
            {
                "warehouse_id": self.warehouse.id,
                "product_id": product.id,
                "company_id": self.warehouse.company_id.id,
                "product_min_qty": 0,
                "product_max_qty": 0,
                "location_id": self.warehouse.lot_stock_id.id,
                "product_uom": product.uom_id.id,
                "supplier_id": seller.id,
            }
        )

    def test_00(self):
        """Test initial context."""
        self.assertFalse(self.product.orderpoint_ids)
        self.assertFalse(self.product2.orderpoint_ids)

    def test_03(self):
        """Test orderpoint selection by supplier."""
        old_lines = self.product.purchase_order_line_ids
        self._create_orderpoint(self.product, self.product_seller)
        self._create_delivery_move(self.product, 100)
        new_lines = self.product.purchase_order_line_ids - old_lines
        new_lines.unlink()
        self.env["procurement.group"].with_context(
            procure_type="by_suppliers", supplier_ids=self.supplier.ids
        ).run_scheduler()
        new_lines = self.product.purchase_order_line_ids - old_lines
        self.assertTrue(new_lines)

    def test_04(self):
        """Test orderpoint is not selected for a different supplier."""
        old_lines = self.product.purchase_order_line_ids
        self._create_orderpoint(self.product, self.product_seller)
        self._create_delivery_move(self.product, 100)
        new_lines = self.product.purchase_order_line_ids - old_lines
        new_lines.unlink()
        self.env["procurement.group"].with_context(
            procure_type="by_suppliers", supplier_ids=self.supplier2.ids
        ).run_scheduler()
        new_lines = self.product.purchase_order_line_ids - old_lines
        self.assertFalse(new_lines)

    @freeze_time("2023-04-03")
    def test_05(self):
        """Test orderpoint is selected for a given day."""
        self._create_orderpoint(self.product, self.product_seller)
        self.supplier.is_manage_day_1 = True
        old_lines = self.product.purchase_order_line_ids
        self._create_delivery_move(self.product, 100)
        new_lines = self.product.purchase_order_line_ids - old_lines
        new_lines.unlink()
        self.env["procurement.group"].with_context(
            procure_type="by_days", is_manage_day_1=True
        ).run_scheduler()
        new_lines = self.product.purchase_order_line_ids - old_lines
        self.assertTrue(new_lines)

    @freeze_time("2023-04-03")
    def test_06(self):
        """Test orderpoint is not selected for a different day."""
        self._create_orderpoint(self.product, self.product_seller)
        self.supplier.is_manage_day_2 = True
        old_lines = self.product.purchase_order_line_ids
        self._create_delivery_move(self.product, 100)
        new_lines = self.product.purchase_order_line_ids - old_lines
        new_lines.unlink()
        self.env["procurement.group"].with_context(
            procure_type="by_days", is_manage_day_1=True
        ).run_scheduler()
        new_lines = self.product.purchase_order_line_ids - old_lines
        self.assertFalse(new_lines)

    @freeze_time("2023-04-03")
    def test_07(self):
        """Test stock scheduler compute wizard, no supplier selected."""
        wizard_form = Form(self.env["stock.scheduler.compute"])
        self.assertEqual(wizard_form.procure_type, "by_suppliers")
        wizard = wizard_form.save()
        with self.assertRaises(UserError):
            wizard.procure_calculation()

    @freeze_time("2023-04-03")
    def test_08(self):
        """Test stock scheduler compute wizard, no day selected."""
        wizard_form = Form(self.env["stock.scheduler.compute"])
        wizard_form.procure_type = "by_days"
        self.assertTrue(wizard_form.is_manage_day_1)
        wizard_form.is_manage_day_1 = False
        wizard = wizard_form.save()
        with self.assertRaises(UserError):
            wizard.procure_calculation()
