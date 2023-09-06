# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.fs_base_multi_media.models import fs_media


class FsMedia(fs_media.FsMedia):

    lang = fields.Selection("_selection_lang", "Language")

    @api.model
    def _selection_lang(self):
        return self.env["res.lang"].get_installed()
