# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestPickingTotal(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        cls.picking_type_obj = cls.env["stock.picking.type"]
        cls.advice_obj = cls.env["shipment.advice"]
        cls.route_obj = cls.env["stock.route"]
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.customers = cls.env.ref("stock.stock_location_customers")
        cls.warehouse.delivery_steps = "pick_ship"
        cls.env.company.shipment_advice_packages_display_mode = "package"
        cls.stock = cls.warehouse.lot_stock_id

        cls.stock_medicament = cls.stock.create(
            {
                "name": "Médicaments",
                "location_id": cls.stock.id,
            }
        )
        cls.stock_aliment = cls.stock.create(
            {
                "name": "Aliments",
                "location_id": cls.stock.id,
            }
        )

        cls.picking_type_medicament = cls.picking_type_obj.create(
            {
                "name": "Médicaments",
                "sequence_code": "MED",
                "code": "internal",
                "default_location_src_id": cls.stock_medicament.id,
                "default_location_dest_id": cls.warehouse.wh_output_stock_loc_id.id,
            }
        )
        cls.picking_type_aliments = cls.picking_type_obj.create(
            {
                "name": "Aliments",
                "sequence_code": "ALI",
                "code": "internal",
                "default_location_src_id": cls.stock_aliment.id,
                "default_location_dest_id": cls.warehouse.wh_output_stock_loc_id.id,
            }
        )

        cls.route_ali = cls.route_obj.create(
            {
                "name": "Aliments",
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Pull Ali",
                            "location_dest_id": cls.warehouse.wh_output_stock_loc_id.id,
                            "location_src_id": cls.stock_aliment.id,
                            "picking_type_id": cls.picking_type_aliments.id,
                            "action": "pull",
                        }
                    )
                ],
            }
        )

        cls.route_medocs = cls.route_obj.create(
            {
                "name": "Médicaments",
                "sequence": 1,
                "rule_ids": [
                    Command.create(
                        {
                            "name": "Pull Médocs",
                            "location_dest_id": cls.warehouse.wh_output_stock_loc_id.id,
                            "location_src_id": cls.stock_medicament.id,
                            "picking_type_id": cls.picking_type_medicament.id,
                            "action": "pull",
                        }
                    )
                ],
            }
        )

        cls.wizard_obj = cls.env["choose.delivery.package"]
        cls.medocs = cls.env["stock.package.type.category"].create(
            {
                "name": "Médicaments",
                "code": "MED",
            }
        )
        cls.aliments = cls.env["stock.package.type.category"].create(
            {
                "name": "Aliments",
                "code": "ALI",
            }
        )
        cls.boite_medocs_1 = cls.env["stock.package.type"].create(
            {
                "name": "Boîte Médicaments 1",
                "category_id": cls.medocs.id,
                "number_of_parcels": 1.0,
            }
        )
        cls.boite_aliments_1 = cls.env["stock.package.type"].create(
            {
                "name": "Boîte Aliments 1",
                "category_id": cls.aliments.id,
                "number_of_parcels": 1.0,
            }
        )

        cls.colis_aliments_1 = cls.env["stock.quant.package"].create(
            {
                "name": "Colis Aliments 1",
                "package_type_id": cls.boite_aliments_1.id,
                "is_internal": True,
            }
        )
        cls.product_medoc = cls.product_obj.create(
            {
                "name": "Product Médicaments Test",
                "type": "product",
                "route_ids": [
                    Command.link(cls.warehouse.delivery_route_id.id),
                    Command.link(cls.route_medocs.id),
                ],
            }
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product_medoc.id,
                "location_id": cls.stock_medicament.id,
                "inventory_quantity": 10.0,
            }
        )._apply_inventory()

        cls.product_aliment = cls.product_obj.create(
            {
                "name": "Product Aliment Test",
                "type": "product",
                "route_ids": [
                    Command.link(cls.warehouse.delivery_route_id.id),
                    Command.link(cls.route_ali.id),
                ],
            }
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.product_aliment.id,
                "location_id": cls.stock_aliment.id,
                "inventory_quantity": 10.0,
            }
        )._apply_inventory()

    def test_delivery(self):
        proc_vals = {}
        self.env["procurement.group"].run(
            [
                self.env["procurement.group"].Procurement(
                    self.product_medoc,
                    5.0,
                    self.product_medoc.uom_id,
                    self.customers,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
                self.env["procurement.group"].Procurement(
                    self.product_aliment,
                    5.0,
                    self.product_aliment.uom_id,
                    self.customers,
                    "Test 1",
                    "Test 1",
                    self.env.company,
                    proc_vals,
                ),
            ]
        )
        pick_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_medoc.id),
                ("location_id", "=", self.stock_medicament.id),
            ]
        )
        self.assertTrue(pick_move)

        wizard = self.wizard_obj.create(
            {
                "picking_id": pick_move.picking_id.id,
                "delivery_package_type_id": self.boite_medocs_1.id,
            }
        )
        wizard.action_put_in_pack()

        self.assertTrue(pick_move.move_line_ids.result_package_id)

        pick_move.picking_id._action_done()

        # Aliments
        pick_ali_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_aliment.id),
                ("location_id", "=", self.stock_aliment.id),
            ]
        )
        self.assertTrue(pick_ali_move)

        pick_ali_move.move_line_ids.result_package_id = self.colis_aliments_1
        pick_ali_move.move_line_ids.qty_done = (
            pick_ali_move.move_line_ids.reserved_uom_qty
        )

        pick_ali_move.picking_id._action_done()

        ship_move = self.env["stock.move"].search(
            [
                ("product_id", "=", self.product_medoc.id),
                ("location_dest_id", "=", self.customers.id),
            ]
        )
        self.assertTrue(pick_move)

        advice = self.advice_obj.create(
            {
                "name": "Test",
                "shipment_type": "outgoing",
            }
        )

        ship_move.picking_id._load_in_shipment(advice)
        result = advice.get_alc_report_shipment_advice()
        result.line_ids.mapped("parcels_and_items_per_category")

        _content, _content_type = self.env["ir.actions.report"]._render_qweb_pdf(
            "shipment_advice.report_shipment_advice", advice.ids, False
        )
