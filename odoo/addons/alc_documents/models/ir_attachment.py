# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.base.models.ir_attachment import IrAttachment


class Attachment(IrAttachment):
    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for record in res:
            self.env["alc.document"].jobify_process_dossier(record)
        return res
