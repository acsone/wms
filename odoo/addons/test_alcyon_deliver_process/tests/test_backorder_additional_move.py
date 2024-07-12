# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import TestDeliverProcessBase


class TestBackorderAdditionalMove(TestDeliverProcessBase):
    def test_backorder_additional(self):
        """
        This will test a flow during which we:

        - Set available quantity for additional product at 50.0 in Stock and 50.0 in Reserve
        - Create a SO with additional product with quantity 100.0
        - Do the pick partially and let the remaining quantity for additional product
        in backorder
        - Try to deliver
        - The process would warn without error that there are remaining quantities
        """
        # Allow backorder for additional product on PICK operations
        self.warehouse_1.pick_type_id.no_backorder_for_additional_product = False
        # Create the reserve location under Warehouse view
        self.reserve = self.env["stock.location"].create(
            {
                "name": "Reserve",
                "location_id": self.warehouse_1.view_location_id.id,
                "usage": "internal",
            }
        )

        # Void the actual quantity
        quant = self.env["stock.quant"].search(
            [
                ("product_id", "=", self.additional_product.id),
                ("location_id", "=", self.loc_stock.id),
            ]
        )
        quant.unlink()

        self.env["stock.quant"]._update_available_quantity(
            self.additional_product, self.loc_stock, 50.0
        )

        self.env["stock.quant"]._update_available_quantity(
            self.additional_product, self.reserve, 50.0
        )

        # create the os, only ship is generated
        sale = self._confirm_sale_order(products=[self.main_product], qty=20.0)
        ship = self._get_picking_ship(sale)
        pick = self._get_picking_pick(sale)
        self.assertEqual(len(ship), 1)
        self.assertEqual(len(pick), 0)
        self.assertEqual(ship.release_channel_id, self.channel)
        # open the channel, pick must be generated
        self.channel.action_unlock()
        pick = self._get_picking_pick(sale)
        ships = self._get_picking_ship(sale).filtered(lambda p: p.state == "waiting")
        self.assertEqual(ships.release_channel_id, self.channel)
        self.assertEqual(pick.release_channel_id, self.channel)
        self.assertEqual(pick.state, "assigned")
        self.channel.action_lock()
        # do the pick
        pick._put_in_pack(pick.move_line_ids)
        # for move_line in pick.move_ids.move_line_ids:
        #     move_line.qty_done -= 1
        pick._action_done()
        self.assertTrue(pick.backorder_ids)

        # shipment_advice = self.env["shipment.advice"].create({
        #     "shipment_type": "outgoing",
        # })
        # ships._load_in_shipment(shipment_advice)

        # Try to deliver with a shipment advice
        # ships._put_in_pack(ships.move_line_ids)
        res = self.channel.action_deliver()
        self.assertEqual(
            "stock.release.channel.deliver.check.wizard", res.get("res_model", False)
        )

        wizard = (
            self.env["stock.release.channel.deliver.check.wizard"]
            .with_context(**res.get("context"))
            .create({})
        )

        wizard.action_deliver()

        self.assertFalse(self.channel.delivering_error)
        self.assertEqual(self.channel.state, "delivered")
