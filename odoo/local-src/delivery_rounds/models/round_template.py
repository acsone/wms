# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class RoundTemplateVersion(models.Model):
    _name = 'round.template.version'

    name = fields.Char('Name', required=True)
    template_ids = fields.Many2many('round.template', string='Templates')
    is_default_version = fields.Boolean('Default version')

    @api.constrains('is_default_version')
    def constrains_is_default_version(self):
        for version in self:
            if not version.is_default_version:
                continue

            default_version = self.search([('is_default_version', '=', True),
                                           ('id', '!=', version.id)])
            if default_version:
                raise UserError(_('You cannot have more '
                                  'than one default version at once.'))


class RoundTemplate(models.Model):
    _name = "round.template"
    _order = "time_leave_planned"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True, default="0")
    itinerary_ids = fields.Many2many(
        'round.itinerary',
        string="Itineraries")
    color = fields.Integer('Color Index')
    time_picking_planned = fields.Float(
        'Planned Picking Start Time')
    time_leave_planned = fields.Float(
        'Planned Vehicle Start Time')

    @api.multi
    @api.depends('name', 'code')
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.code + ' - ' + rec.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            vals = name.split('-', 1)
            if len(vals) > 1:
                code = vals[0].strip()
                text = vals[1].strip()
                comb = operator.startswith('not ') and '|' or '&'
            else:
                code = text = name.strip()
                comb = operator.startswith('not ') and '&' or '|'
            domain = [
                comb,
                ('code', operator, code),
                ('name', operator, text)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()
