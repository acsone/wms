# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrTranslation(models.Model):

    _inherit = "ir.translation"

    @api.model_cr_context
    def _auto_init(self):
        res = super(IrTranslation, self)._auto_init()
        cr = self._cr

        cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname LIKE "
            "'ir_translation_%'"
        )
        indexes = [row[0] for row in cr.fetchall()]
        if "ir_translation_name_lang_res_id_id_idx" in indexes:
            # drop test index
            cr.execute("DROP INDEX ir_translation_name_lang_res_id_id_idx")

        if "ir_translation_name_lang_type_res_id_idx" not in indexes:
            cr.execute(
                "CREATE INDEX ir_translation_name_lang_type_res_id_idx "
                "ON ir_translation(name, lang, type, res_id) WHERE "
                "value != ''"
            )

        return res
