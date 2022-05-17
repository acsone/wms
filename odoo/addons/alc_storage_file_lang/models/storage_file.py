# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StorageFile(models.Model):
    _inherit = "storage.file"

    lang = fields.Selection("_selection_lang", "Language")

    @api.model
    def _selection_lang(self):
        return self.env["res.lang"].get_installed()
