# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AbstractUrlLocal(models.AbstractModel):

    _name = "abstract.url.local"
    _description = "Abstract Url Local"

    @property
    def url_key_locales(self):
        res = {}
        for binding in self.se_binding_ids:
            binding = binding._contextualize(binding)
            if binding.record.url_key:
                if not binding.index_id.lang_id:
                    continue
                res[binding.index_id.lang_id.code] = binding.record.url_key
        return res
