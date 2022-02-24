# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductBrand(models.Model):

    _inherit = "product.brand"
    image_id = fields.Many2one(string="storage image", comodel_name="storage.image")

    logo = fields.Binary(compute="_compute_logo", inverse="_inverse_logo")
    logo_filename = fields.Char(related="image_id.name")
    image_url = fields.Char(related="image_id.url")
    image_small_url = fields.Char(related="image_id.image_small_url")
    image_medium_url = fields.Char(related="image_id.image_medium_url")

    @api.depends("image_id")
    def _compute_logo(self):
        for rec in self:
            rec.logo = rec.image_id.data

    def _inverse_logo(self):
        for rec in self:
            logo = rec.logo
            if rec.image_id:
                rec.image_id.unlink()
            if not logo:
                continue
            rec.image_id = rec.image_id.create(
                {
                    "backend_id": rec._get_default_backend_id(),
                    "name": rec.logo_filename or rec.name,
                    "data": logo,
                }
            )

    def _get_default_backend_id(self):
        return self.env["storage.backend"]._get_backend_id_from_param(
            self.env, "storage.image.backend_id"
        )

    def unlink(self):
        self.mapped("image_id").unlink()
        return super(ProductBrand, self).unlink()
