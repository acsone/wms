# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MakePickingBatch(models.TransientModel):

    _inherit = "make.picking.batch"
    picking_type_ids = fields.Many2many(domain="[('subcode','=','PICK')]")

    def _compute_device_to_use(self, first_picking_to_cluster):
        recommended_device = None
        palette = self.env.ref(
            "alc_stock_picking_batch_creation.palette", raise_if_not_found=False
        )
        use_palette = self.env.ref(
            "alc_stock_picking_batch_creation.res_partner_category_deliver_pal",
            raise_if_not_found=False,
        )
        picking_ali = self.env.ref(
            "__setup__.stock_picking_type_ali", raise_if_not_found=False
        )

        partner = first_picking_to_cluster.partner_id
        if (
            partner.category_id == use_palette
            or partner.parent_id.category_id == use_palette
            and self.picking_type_ids in [picking_ali]
        ):
            recommended_device = palette

        return (
            recommended_device
            if recommended_device
            else super(MakePickingBatch, self)._compute_device_to_use(
                first_picking_to_cluster
            )
        )
