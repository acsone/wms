# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RoundTag(models.Model):
    _name = 'round.tag'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    color = fields.Integer('Color Index')

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            if not self.env.context.get('short_round_tag_name'):
                name = rec.name
            else:
                name = rec.code or rec.name
            result.append((rec.id, name))
        return result
