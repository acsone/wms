# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.fs_base_multi_media.models import fs_media_relation_mixin


class FsMediaRelationMixin(fs_media_relation_mixin.FsMediaRelationMixin):

    lang = fields.Selection(
        "_selection_lang",
        "Language",
        compute="_compute_lang",
        readonly=False,
        store=True,
    )

    @api.model
    def _selection_lang(self):
        return self.env["res.lang"].get_installed()

    @api.depends("media_id", "media_id.lang", "specific_file", "link_existing")
    def _compute_lang(self):
        for record in self:
            if record.link_existing:
                record.lang = record.media_id.lang
