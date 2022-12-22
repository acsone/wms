# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StorageBackend(models.Model):
    _inherit = "storage.backend"

    def action_recompute_base_url_for_files(self):
        res = super(StorageBackend, self).action_recompute_base_url_for_files()
        self._recompute_stored_url_for_files()
        return res

    def _recompute_stored_url_for_files(self):
        self._recompute_stored_url_for_files_odoo()
        self._recompute_stored_url_for_files_external()

    def _recompute_stored_url_for_files_odoo(self):
        to_recompute = self.filtered(lambda b: b.served_by == "odoo")
        if to_recompute:
            odoo_root = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
            query = """
            UPDATE storage_file sf
            SET url = CONCAT(%s, 'storage.file', sf.slug)
            FROM storage_backend sb
            WHERE sf.backend_id IN %s AND sf.backend_id = sb.id
            """
            self.env.cr.execute(query, (odoo_root, tuple(to_recompute.ids)))

    def _recompute_stored_url_for_files_external(self):
        to_recompute = self.filtered(lambda b: b.served_by != "odoo")
        if to_recompute:
            query = """
            UPDATE storage_file sf
            SET url = CONCAT(sb.base_url_for_files, sf.relative_path)
            FROM storage_backend sb
            WHERE sf.backend_id IN %s AND sf.backend_id = sb.id
            """
            self.env.cr.execute(query, (tuple(to_recompute.ids),))
