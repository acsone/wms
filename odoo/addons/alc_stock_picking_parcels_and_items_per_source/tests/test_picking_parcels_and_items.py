# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase

from .common import PickingParcelsItemsCommon


class TestPickingTotal(PickingParcelsItemsCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        test_carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.test_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "delivery_type": "fixed",
                "product_id": test_carrier_product.id,
            }
        )
        cls.package_type = cls.env["stock.package.type"].create(
            {
                "name": "package type",
                "number_of_parcels": 7,
            }
        )

        cls.pharma_type.set_delivery_package_type_on_put_in_pack = True
        cls.food_type.set_delivery_package_type_on_put_in_pack = True
        cls.warehouse.pick_type_id.set_delivery_package_type_on_put_in_pack = True

    def _put_in_pack(self, picking):
        picking.group_id.carrier_id = self.test_carrier

        pack_action = picking.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        pack_action_model = pack_action["res_model"]
        # We make sure the correct action was returned
        self.assertEqual(pack_action_model, "choose.delivery.package")
        # check there is no package yet for the picking
        self.assertEqual(len(picking.package_ids), 0)
        # We instanciate the wizard with the context of the action
        pack_wiz = (
            self.env["choose.delivery.package"]
            .with_context(**pack_action_ctx)
            .create({})
        )
        # set the package type
        pack_wiz.delivery_package_type_id = self.package_type
        pack_wiz.action_put_in_pack()

    def _get_jsonb(self, json_value):
        # As integer keys have been converted to string.
        final = {}
        for key, value in json_value.items():
            final[int(key)] = value
        return final

    def test_flow(self):
        self._create_customer_need()
        self.picking_out = self.Picking.search(
            [
                ("move_ids.product_id", "in", self.products.ids),
                ("picking_type_id", "=", self.warehouse.out_type_id.id),
            ]
        )
        self.picking_out.carrier_id = self.test_carrier
        # Transfer Pharma Picking
        pick_picking_pharma = self.Picking.search(
            [
                ("product_id", "=", self.pharma_product.id),
                ("location_dest_id", "=", self.warehouse.wh_pack_stock_loc_id.id),
            ]
        )
        for move in pick_picking_pharma.move_ids:
            move.quantity_done = move.product_uom_qty
        self._put_in_pack(pick_picking_pharma)
        pick_picking_pharma._action_done()
        self.assertEqual("done", pick_picking_pharma.state)

        # Transfer Food Picking
        pick_picking_food = self.Picking.search(
            [
                ("product_id", "=", self.food_product.id),
                ("location_dest_id", "=", self.warehouse.wh_pack_stock_loc_id.id),
            ]
        )
        for move in pick_picking_food.move_ids:
            move.quantity_done = move.product_uom_qty
        self._put_in_pack(pick_picking_food)
        pick_picking_food._action_done()
        self.assertEqual("done", pick_picking_food.state)

        # Transfer Normal Picking
        pick_picking_normal = self.Picking.search(
            [
                ("product_id", "=", self.normal_product.id),
                ("location_dest_id", "=", self.warehouse.wh_pack_stock_loc_id.id),
            ]
        )
        for move in pick_picking_normal.move_ids:
            move.quantity_done = move.product_uom_qty
        # self._put_in_pack(pick_picking_normal)
        pick_picking_normal._action_done()
        self.assertEqual("done", pick_picking_normal.state)

        pack_picking = self.Picking.search(
            [
                ("product_id", "=", self.pharma_product.id),
                ("location_dest_id", "=", self.warehouse.wh_output_stock_loc_id.id),
            ]
        )
        for move in pack_picking.move_ids:
            move.quantity_done = move.product_uom_qty
        pack_picking._action_done()
        self.assertEqual("done", pack_picking.state)
        picking_ship = self.Picking.search(
            [
                ("product_id", "=", self.pharma_product.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        for move in picking_ship.move_ids:
            move.quantity_done = move.product_uom_qty
        picking_ship._action_done()

        self.assertDictEqual(
            {self.env.ref("stock.stock_location_stock").id: 6.0},
            self._get_jsonb(picking_ship.parcels_and_items_per_source["items"]),
        )
        self.assertDictEqual(
            {
                self.pharma_location.id: 7.0,
                self.food_location.id: 7.0,
            },
            self._get_jsonb(picking_ship.parcels_and_items_per_source["parcels"]),
        )
        self.assertEqual(14, picking_ship.parcels_and_items_per_source["parcels_total"])
        self.assertEqual(6.0, picking_ship.parcels_and_items_per_source["items_total"])
