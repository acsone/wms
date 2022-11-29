# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MixinFileId(models.AbstractModel):

    _name = "mixin.file.id"

    file_id = fields.Many2one(string="storage file", comodel_name="storage.file")
    file = fields.Binary(compute="_compute_file", inverse="_inverse_file")
    filename = fields.Char()  # should not be a computed field

    @api.depends("file_id")
    def _compute_file(self):
        for rec in self:
            rec.file = rec.file_id.data

    def _inverse_file(self):
        for rec in self:
            new_file = rec.file
            if rec.file_id:
                rec.file_id.with_context(cleanning_storage_file=True).unlink()
            if not new_file:
                rec.file_id = None
                rec.filename = None
            else:
                vals_file = {"name": rec.filename or rec.name, "data": new_file}
                rec.file_id = self._create_file_id(vals_file)

    @api.model
    def _create_file_id(self, vals):
        if "backend_id" not in vals:
            vals["backend_id"] = self._get_default_backend_id()
        return self.env["storage.file"].create(vals)

    @api.model
    def _get_default_backend_id(self):
        return self.env["storage.backend"]._get_backend_id_from_param(
            self.env, "storage.image.backend_id"
        )

    def unlink(self):
        self.mapped("file_id").unlink()
        return super(MixinFileId, self).unlink()
