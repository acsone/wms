# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MixinImageId(models.AbstractModel):

    _name = "mixin.image.id"

    image_id = fields.Many2one(string="storage image", comodel_name="storage.image",)
    image = fields.Binary(
        compute="_compute_image", inverse="_inverse_image", required=True
    )
    image_filename = fields.Char(related="image_id.name")
    image_url = fields.Char(related="image_id.url")
    image_small_url = fields.Char(related="image_id.image_small_url")
    image_medium_url = fields.Char(related="image_id.image_medium_url")

    @api.model
    def _get_default_image_backend_id(self):
        return self.env["storage.backend"]._get_backend_id_from_param(
            self.env, "storage.image.backend_id"
        )

    @api.depends("image_id")
    def _compute_image(self):
        for rec in self:
            rec.image = rec.image_id.data

    def _inverse_image(self):
        for rec in self:
            new_image = rec.image
            if rec.image_id:
                rec.image_id.unlink()
            if not new_image:
                continue
            rec.image_id = rec.image_id.create(
                {
                    "backend_id": rec._get_default_image_backend_id(),
                    "name": rec.image_filename or rec.name,
                    "data": new_image,
                }
            )
