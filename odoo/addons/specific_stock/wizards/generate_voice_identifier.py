# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class GenerateVoiceIdentifier(models.TransientModel):
    _name = "generate.voice.identifier"

    lot_ids = fields.Many2many("stock.production.lot", string="Lots")

    def default_get(self, fields_list=None):
        if not fields_list:
            fields_list = {}
        result = super(GenerateVoiceIdentifier, self).default_get(
            fields_list=fields_list
        )

        result["lot_ids"] = [(6, 0, self.env.context.get("active_ids", []))]

        return result

    @api.multi
    def generate_voice_identifier(self):
        self.ensure_one()

        lots = self.lot_ids
        lots.with_context(force_compute=True).compute_voice_identifier()
