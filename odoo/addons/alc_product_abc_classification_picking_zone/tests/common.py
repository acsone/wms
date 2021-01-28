# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.product_abc_classification_base.tests import common


class AclAbcClassificationProfilePickingZoneBase(common.ABCClassificationLevelCase):
    @classmethod
    def setUpClass(cls):
        super(AclAbcClassificationProfilePickingZoneBase, cls).setUpClass()
        # We create 2 zones, 2 picking types for each zone and 2 stock.location.route
        # for each picking_type.
        # These infos are required to be able to put a picking_zone on a product
        # since the picking zone comes from the route
        PickingZone = cls.env["picking.zone"]
        PickingType = cls.env["stock.picking.type"]
        cls.zone_ali = PickingZone.create({"name": "Aliments", "code": "01"})
        cls.zone_med = PickingZone.create({"name": "Med", "code": "02"})
        wh = cls.env.ref("stock.warehouse0")
        picking_sequence = wh.in_type_id.sequence_id
        stock_location = cls.env.ref("stock.stock_location_stock")

        cls.picking_type_ali = PickingType.create(
            {
                "name": "Pick Aliments",
                "code": "internal",
                "picking_zone_id": cls.zone_ali.id,
                "sequence_id": picking_sequence.id,
                "default_location_src_id": stock_location.id,
            }
        )
        cls.picking_type_med = PickingType.create(
            {
                "name": "Pick Med",
                "code": "internal",
                "picking_zone_id": cls.zone_med.id,
                "sequence_id": picking_sequence.id,
                "default_location_src_id": stock_location.id,
            }
        )
        location_out = cls.env.ref("stock.stock_location_output")
        cls.route_aliment = cls.env["stock.location.route"].create(
            {
                "name": "Aliments",
                "pull_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "pull_ali",
                            "location_id": location_out.id,
                            "picking_type_id": cls.picking_type_ali.id,
                            "location_src_id": stock_location.id,
                            "procure_method": "make_to_stock",
                            "action": "move",
                        },
                    )
                ],
            }
        )

        cls.route_medoc = cls.env["stock.location.route"].create(
            {
                "name": "Aliments",
                "pull_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "pull_medoc",
                            "location_id": location_out.id,
                            "picking_type_id": cls.picking_type_med.id,
                            "location_src_id": stock_location.id,
                            "procure_method": "make_to_stock",
                            "action": "move",
                        },
                    )
                ],
            }
        )
        cls.product_aliment = cls.env["product.product"].create(
            {
                "name": "Alim",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
                "route_ids": [(6, 0, cls.route_aliment.ids)],
            }
        )
        cls.product_medoc = cls.env["product.product"].create(
            {
                "name": "Medoc",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 20.0,
                "route_ids": [(6, 0, cls.route_medoc.ids)],
            }
        )
        cls.no_route_product = cls.env["product.product"].create(
            {
                "name": "No route",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "weight": 10.0,
            }
        )
