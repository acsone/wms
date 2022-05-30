# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class IrAttachment(models.Model):

    _inherit = "ir.attachment"

    storage_image_id = fields.Many2one(comodel_name="storage.image", string="Image")

    def _publish_to_storage_image(self):
        for rec in self:
            if not rec.storage_image_id:
                vals_img = {
                    "name": rec.name,
                    "file_type": "image",
                    "alt_name": rec.name,
                    "data": rec.datas,
                    "mimetype": rec.mimetype,
                }
                rec.storage_image_id = self.env["storage.image"].create(vals_img)
