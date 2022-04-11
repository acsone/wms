# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):

    _inherit = "product.product"

    @api.model
    def _get_es_index(self, lang_code=False, strict_lang=True):
        # we currently assume to have only one backend
        # to make this a mixin, binding model should be obtained from a function
        domain_model = [("model", "=", "shopinvader.variant")]
        model_id = self.env["ir.model"].search(domain_model).id
        lang_code = lang_code or "en_US"
        lang_id = self.env["res.lang"].search([("code", "=", lang_code)]).id
        domain_model = [("model_id", "=", model_id)]
        domain = domain_model + [("lang_id", "=", lang_id)]
        index = self.env["se.index"].search(domain)
        if not index:
            if strict_lang:
                raise ValidationError(_("No index found for lang %s."), lang_code)
            index = self.env["se.index"].search(domain_model, limit=1)
        if not index:
            raise ValidationError(_("No index found."))
        return index

    def _get_products_from_es_cache(
        self, lang_code=False, strict_lang=True, es_params=None, params=None
    ):
        index = self._get_es_index(lang_code=lang_code, strict_lang=strict_lang)
        adapter = index._get_backend_adapter()
        return adapter.search(es_params=es_params, params=params)
