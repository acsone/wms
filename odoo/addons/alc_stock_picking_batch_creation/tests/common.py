# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.stock_picking_batch_creation.tests.common import (
    ClusterPickingCommonFeatures,
)


class AlcClusterPickingCommonFeatures(ClusterPickingCommonFeatures):
    @classmethod
    def setUpClass(cls):
        super(AlcClusterPickingCommonFeatures, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.env["stock.location"]._parent_store_compute()
        picking_sequence = cls.warehouse_1.pick_type_id.sequence_id
        location_out = cls.env.ref("stock.stock_location_output")

        cls.warehouse_1.pick_type_id.subcode = "PICK"
        cls.warehouse_1.delivery_steps = "pick_ship"

        cls.device1.min_volume_liter = 10000
        cls.device2.min_volume_liter = 70000
        cls.device3.min_volume_liter = 30000

        cls.device1.max_volume_liter = 50000
        cls.device2.max_volume_liter = 190000
        cls.device3.max_volume_liter = 100000

        cls.picking_type_medoc = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Médicaments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "subcode": "PICK",
                "color": 7,
                "sequence": 4,
                "stock_device_type_ids": [
                    (4, cls.device4.id),
                    (4, cls.device5.id),
                    (4, cls.device6.id),
                ],
            }
        )

        cls.picking_type_ali = cls.env["stock.picking.type"].create(
            {
                "name": "Pick Aliments",
                "code": "internal",
                "sequence_id": picking_sequence.id,
                "default_location_src_id": cls.stock_location.id,
                "default_location_dest_id": location_out.id,
                "subcode": "PICK",
                "color": 7,
                "sequence": 4,
                "stock_device_type_ids": [
                    (4, cls.device1.id),
                    (4, cls.device2.id),
                    (4, cls.device3.id),
                ],
            }
        )
        cls.env["ir.model.data"].create(
            {
                "module": "__setup__",
                "name": "stock_picking_type_ali",
                "model": "stock.picking.type",
                "res_id": cls.picking_type_ali.id,
            }
        )
