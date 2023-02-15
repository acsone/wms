# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MakePickingBatch(models.TransientModel):

    _inherit = "make.picking.batch"
    picking_type_ids = fields.Many2many(domain="[('subcode','=','PICK')]")

    def _compute_device_to_use(self, first_picking_to_cluster):
        partner = first_picking_to_cluster.partner_id
        partner_devices = partner._get_specific_stock_devices()
        if partner_devices:
            # Initialize dimension fields on picking
            first_picking_to_cluster = first_picking_to_cluster.with_prefetch()
            first_picking_to_cluster._init_dimension_fields()
            menu_devices = self.stock_device_type_ids
            device_to_keep = self.env["stock.device.type"]
            for device in partner_devices:
                if device in menu_devices:
                    device_to_keep |= device

            if device_to_keep:
                # Only one device should be put by zone on the partner
                return device_to_keep[0]
        return super(MakePickingBatch, self)._compute_device_to_use(
            first_picking_to_cluster
        )

    def _lock_selected_picking(self, picking):
        self.env.cr.execute(
            """
            SELECT
                id
            FROM
                stock_picking
            WHERE
                id = %s
            FOR UPDATE OF stock_picking SKIP LOCKED;
        """,
            (picking.id,),
        )
        _id = [r[0] for r in self.env.cr.fetchall()]
        if _id:
            return super(MakePickingBatch, self)._lock_selected_picking(picking)
        return None
