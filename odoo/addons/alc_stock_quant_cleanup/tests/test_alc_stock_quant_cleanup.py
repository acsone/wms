# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestAlcStockQuantCleanup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Product", "type": "product"}
        )
        cls.pick_type = cls.env.ref("stock.picking_type_out")
        cls.loc_customer = cls.env.ref("stock.stock_location_customers")
        cls.location = cls.env.ref("stock.stock_location_stock")
        cls.package = cls.env["stock.quant.package"].create({})
        cls.env["stock.quant"]._update_available_quantity(
            cls.product, cls.location, 5, package_id=cls.package
        )
        cls.picking = cls._create_picking(cls.package)

    @classmethod
    def _create_picking(cls, package):
        picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.pick_type.id,
                "location_id": cls.location.id,
                "location_dest_id": cls.loc_customer.id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "move 1",
                            "product_id": cls.product.id,
                            "product_uom_qty": 5,
                            "location_id": cls.location.id,
                            "location_dest_id": cls.loc_customer.id,
                        },
                    )
                ],
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.action_set_quantities_to_reservation()
        picking.move_line_ids.write(
            {"package_id": package.id, "result_package_id": package.id}
        )
        return picking

    def _quants_in_stock_location(self):
        return self.product.stock_quant_ids.filtered(
            lambda q, l=self.location: q.location_id == l
        )

    @property
    def len_quants_in_stock_location(self):
        return len(self._quants_in_stock_location())

    @property
    def sum_quants_in_stock_location(self):
        return sum(self._quants_in_stock_location().mapped("quantity"))

    def test_0(self):
        """Ensure test context."""
        self.assertEqual(self.len_quants_in_stock_location, 1)
        self.assertEqual(self.sum_quants_in_stock_location, 5)
        self.assertEqual(len(self.package.quant_ids), 1)
        self.assertEqual(self.picking.state, "assigned")
        self.assertEqual(self.picking.move_line_ids.package_id, self.package)
        self.assertEqual(self.picking.move_line_ids.result_package_id, self.package)

    def test_01(self):
        """Ensure zero quant is not removed by picking actions."""
        self.picking._action_done()
        self.assertEqual(self.len_quants_in_stock_location, 1)
        self.assertEqual(self.sum_quants_in_stock_location, 0)

    def test_02(self):
        """Ensure zero quant is removed by picking actions if we force the context key."""
        self.picking.with_context(unlink_zero_quants=True)._action_done()
        self.assertEqual(self.len_quants_in_stock_location, 0)
        self.assertEqual(self.sum_quants_in_stock_location, 0)

    def test_03(self):
        """Ensure _unlink_zero_quants is still called by quant tasks."""
        self.test_01()
        self.assertEqual(self.len_quants_in_stock_location, 1)
        self.assertEqual(self.sum_quants_in_stock_location, 0)
        self.env["stock.quant"]._quant_tasks()
        self.assertEqual(self.len_quants_in_stock_location, 0)

    def test_04(self):
        """Ensure the cron clean up zero quants correctly."""
        self.test_01()
        self.assertEqual(self.len_quants_in_stock_location, 1)
        self.assertEqual(self.sum_quants_in_stock_location, 0)
        cron = self.env.ref("alc_stock_quant_cleanup.alc_stock_quant_cleanup_cron")
        cron.with_context(queue_job__no_delay=True).method_direct_trigger()
        self.assertEqual(self.len_quants_in_stock_location, 0)

    def test_05(self):
        """Ensure picking validation is not impacted by the 0 quant."""
        self.test_01()
        package1 = self.env["stock.quant.package"].create({})
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 5, package_id=package1
        )
        self.assertEqual(self.len_quants_in_stock_location, 2)
        self.assertEqual(self.sum_quants_in_stock_location, 5)
        picking = self._create_picking(package1)
        picking._action_done()
        self.assertEqual(self.len_quants_in_stock_location, 2)
        self.assertEqual(self.sum_quants_in_stock_location, 0)
        package2 = self.env["stock.quant.package"].create({})
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.location, 5, package_id=package2
        )
        self.assertEqual(self.len_quants_in_stock_location, 3)
        self.assertEqual(self.sum_quants_in_stock_location, 5)
        picking = self._create_picking(package2)
        picking._action_done()
        self.assertEqual(self.len_quants_in_stock_location, 3)
        self.assertEqual(self.sum_quants_in_stock_location, 0)
        cron = self.env.ref("alc_stock_quant_cleanup.alc_stock_quant_cleanup_cron")
        cron.with_context(queue_job__no_delay=True).method_direct_trigger()
        self.assertEqual(self.len_quants_in_stock_location, 0)
