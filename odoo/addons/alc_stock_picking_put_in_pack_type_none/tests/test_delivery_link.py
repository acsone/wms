# Copyright 2021-2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo_test_helper import FakeModelLoader

from odoo.addons.stock_picking_delivery_link.tests.common import (
    StockPickingDeliveryLinkCommonCase,
)


class TestStockPickingDeliveryLink(StockPickingDeliveryLinkCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        # pylint: disable=import-outside-toplevel
        from odoo.addons.stock_picking_delivery_link.tests.models.delivery_carrier import (
            DeliveryCarrier,
        )

        cls.loader.update_registry((DeliveryCarrier,))

        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "product"}
        )
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        test_carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.test_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                # This is the case we want to test: the delivery_type is
                # not the default value (fixed)
                "delivery_type": "test",
                "product_id": test_carrier_product.id,
            }
        )
        cls.out_loc = cls.env.ref("stock.stock_location_output")

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_put_in_pack_from_pick_with_wizard(self):
        """
        Normally the "choose package type" wizard is triggered only if a carrier is.

        set on the picking (usually on ship picking). This module permits to force
        the wizard if there is no carrier set but if there is a shipping carrier and
        set_delivery_package_type_on_put_in_pack set on the package type.
        """
        self.wh.delivery_steps = "pick_ship"
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.shelf1_loc, 20.0
        )
        ship_move = self.env["stock.move"].create(
            {
                "name": "The ship move",
                "product_id": self.product.id,
                "product_uom_qty": 5.0,
                "product_uom": self.product.uom_id.id,
                "location_id": self.out_loc.id,
                "location_dest_id": self.customer_location.id,
                "warehouse_id": self.wh.id,
                "picking_type_id": self.wh.out_type_id.id,
                "procure_method": "make_to_order",
                "state": "draft",
            }
        )
        ship_move._assign_picking()
        ship_picking = ship_move.picking_id
        # set a carrier on shipment picking
        ship_picking.carrier_id = self.test_carrier
        ship_move._action_confirm()
        pick_move = ship_move.move_orig_ids[0]
        pick_picking = pick_move.picking_id

        # force wizard on pick operation picking_type_id
        pick_picking.picking_type_id.update(
            {
                "set_delivery_package_type_on_put_in_pack": True,
                "delivery_package_type_none_on_put_in_pack": True,
            }
        )

        pick_picking.action_assign()
        pick_picking.move_line_ids.filtered(
            lambda ml: ml.product_id == self.product
        ).qty_done = 5.0
        pip_action = pick_picking.action_put_in_pack()
        # check the action is a dict
        self.assertIsInstance(pip_action, dict)
        pip_action_model = pip_action["res_model"]
        pip_action_context = pip_action["context"]
        # We make sure the correct action was returned
        self.assertEqual(pip_action_model, "choose.delivery.package")
        self.assertEqual("none", pip_action_context.get("current_package_carrier_type"))
