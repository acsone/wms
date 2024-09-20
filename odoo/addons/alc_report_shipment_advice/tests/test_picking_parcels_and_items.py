# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import TransactionCase

from odoo.addons.alc_stock_picking_parcels_and_items_per_source.tests.common import (
    PickingParcelsItemsCommon,
)


class TestPickingTotal(PickingParcelsItemsCommon, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.advice_obj = cls.env["shipment.advice"]
        # Set Stock location as no source to have a 'false' value
        cls.warehouse.lot_stock_id.is_considered_as_source = False
        cls.pharma_location.sequence_in_shipment_advice_report = 1
        cls.food_location.sequence_in_shipment_advice_report = 2

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

        # Create Shipment Advice
        advice = self.advice_obj.create(
            {
                "name": "Test",
                "shipment_type": "outgoing",
            }
        )

        picking_ship._load_in_shipment(advice)

        self.assertDictEqual(
            {
                "total_parcels": 14.0,
                "total_items": 6.0,
                "total": 20.0,
            },
            advice.parcels_and_items_per_source,
        )

        report = advice.get_alc_report_shipment_advice()
        # Locations are sorted
        self.assertEqual(report.location_ids[1], self.pharma_location)
        self.assertEqual(report.location_ids[2], self.food_location)

        self.assertEqual(report.shipment_advice_id, advice)
        self.assertIn(self.food_location.id, report.location_ids._ids)
        self.assertIn(self.pharma_location.id, report.location_ids._ids)
        self.assertIn(False, report.location_ids._ids)

        paips = report.parcels_and_items_per_source
        self.assertEqual(paips["total_parcels"], 14)
        self.assertEqual(paips["total_items"], 6)
        self.assertEqual(paips["total"], 20)
        paips_zone = paips["total_zone"]
        self.assertEqual(paips_zone[str(self.pharma_location.id)], 7)
        self.assertEqual(paips_zone[str(self.food_location.id)], 7)
        self.assertEqual(paips_zone["false"], 6)
        paips_zone_items = paips["total_zone_items"]
        self.assertEqual(paips_zone_items[str(self.pharma_location.id)], 0)
        self.assertEqual(paips_zone_items[str(self.food_location.id)], 0)
        self.assertEqual(paips_zone_items["false"], 6)
        paips_zone_parcels = paips["total_zone_parcels"]
        self.assertEqual(paips_zone_parcels[str(self.pharma_location.id)], 7)
        self.assertEqual(paips_zone_parcels[str(self.food_location.id)], 7)
        self.assertEqual(paips_zone_parcels["false"], 0)

        # Check if report is correctly generated
        _content, _content_type = self.env["ir.actions.report"]._render_qweb_pdf(
            "shipment_advice.report_shipment_advice", advice.ids, False
        )

    def test_flow_without_pharma(self):
        # The Pharma zone location is not set as source
        self.pharma_location.is_considered_as_source = False
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

        # Create Shipment Advice
        advice = self.advice_obj.create(
            {
                "name": "Test",
                "shipment_type": "outgoing",
            }
        )

        picking_ship._load_in_shipment(advice)

        self.assertDictEqual(
            {
                "total_parcels": 14.0,
                "total_items": 6.0,
                "total": 20.0,
            },
            advice.parcels_and_items_per_source,
        )

        report = advice.get_alc_report_shipment_advice()

        self.assertEqual(report.shipment_advice_id, advice)
        self.assertIn(self.food_location.id, report.location_ids._ids)
        self.assertIn(False, report.location_ids._ids)

        paips = report.parcels_and_items_per_source
        self.assertEqual(paips["total_parcels"], 14)
        self.assertEqual(paips["total_items"], 6)
        self.assertEqual(paips["total"], 20)
        paips_zone = paips["total_zone"]
        self.assertEqual(paips_zone[str(self.food_location.id)], 7)
        self.assertEqual(paips_zone["false"], 13)
        paips_zone_items = paips["total_zone_items"]
        self.assertEqual(paips_zone_items[str(self.food_location.id)], 0)
        self.assertEqual(paips_zone_items["false"], 6)
        paips_zone_parcels = paips["total_zone_parcels"]
        self.assertEqual(paips_zone_parcels[str(self.food_location.id)], 7)
        self.assertEqual(paips_zone_parcels["false"], 7)

        # Check if report is correctly generated
        _content, _content_type = self.env["ir.actions.report"]._render_qweb_pdf(
            "shipment_advice.report_shipment_advice", advice.ids, False
        )

    def test_flow_package_category(self):
        """Create."""
        self._create_customer_need()
        self.picking_out = self.Picking.search(
            [
                ("move_ids.product_id", "in", self.products.ids),
                ("picking_type_id", "=", self.warehouse.out_type_id.id),
            ]
        )
        self.picking_out.carrier_id = self.test_carrier
        # Transfer Pharma Picking
        self.Picking.search(
            [
                ("product_id", "=", self.pharma_product.id),
                ("location_dest_id", "=", self.warehouse.wh_pack_stock_loc_id.id),
            ]
        )
