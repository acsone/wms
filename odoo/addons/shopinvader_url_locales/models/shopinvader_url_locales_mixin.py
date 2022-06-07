# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import api, fields, models


class ShopinvaderUrlLocalesMixin(models.AbstractModel):

    # Concrete models must _inherit = ["shopinvader.binding", "abstract.url"]
    _name = "shopinvader.url.locales.mixin"
    _description = "Shopinvader Url Locales"

    url_key_locales = fields.Serialized(compute="_compute_url_key_locales")

    @api.depends(lambda self: self._url_key_locales_depends())
    def _compute_url_key_locales(self):
        backend_ids = self.mapped("backend_id").ids
        result = {bid: defaultdict(dict) for bid in backend_ids}
        for (
            backend_id,
            binding_ids_by_lang_id,
        ) in self._get_bindings_by_lang_by_backend().items():
            result_by_backend_id = result[backend_id]
            for lang_id, binding_ids in binding_ids_by_lang_id.items():
                lang = self.env["res.lang"].browse(lang_id)
                bindings = (
                    self.with_prefetch(None)
                    .browse(binding_ids)
                    .with_context(lang=lang.code)
                )
                for binding in bindings:
                    result_by_backend_id[binding.record_id.id][
                        lang.code
                    ] = binding.url_key
        for rec in self:
            rec.url_key_locales = result[rec.backend_id.id][rec.record_id.id]

    def _get_bindings_by_lang_by_backend(self):
        """Return a dict of binding ids by lang id and by backend id"""
        return {}

    @api.model
    def _url_key_locales_depends(self):
        return []
