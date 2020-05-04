# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models

from .utils import create_index, install_trgm_extension


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    url = fields.Char(index=True)

    @api.model_cr
    def init(self):
        trgm_installed = install_trgm_extension(self.env)
        self.env.cr.commit()

        if trgm_installed:
            index_name = "ir_attachment_url_trgm_index"
            create_index(
                self.env.cr, index_name, self._table, "USING gin (url gin_trgm_ops)"
            )
