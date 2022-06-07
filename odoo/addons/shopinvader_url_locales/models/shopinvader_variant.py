# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, models


class ShopinvaderVariant(models.Model):

    _name = "shopinvader.variant"
    _inherit = ["shopinvader.variant", "shopinvader.url.locales.mixin"]

    def _get_bindings_by_lang_by_backend(self):
        """Return a dict of binding ids by lang id and by backend id"""
        backend_ids = self.mapped("backend_id").ids
        result = {_id: defaultdict(list) for _id in backend_ids}
        self.env.cr.execute(
            """
            SELECT
                array_agg(sv.id || ',' || sp.lang_id ),
                backend_id
            FROM
                shopinvader_variant sv
                JOIN shopinvader_product sp
                ON sp.id = sv.shopinvader_product_id
            WHERE
                sv.active
                AND sv.record_id in %s
                AND backend_id in %s
            GROUP BY
                sv.record_id, backend_id
        """,
            (tuple(self.mapped("record_id.id")), tuple(backend_ids),),
        )
        for row in self.env.cr.fetchall():
            bindings = row[0]
            backend_id = row[1]
            info = result[backend_id]
            for binding_id_lang_id in bindings:
                binding_id, lang_id = binding_id_lang_id.split(",")
                info[int(lang_id)].append(int(binding_id))
        return result

    @api.model
    def _url_key_locales_depends(self):
        return ["url_key", "lang_id", "record_id.shopinvader_bind_ids"]
