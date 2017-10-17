# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class RoundItinerary(models.Model):
    _name = 'round.itinerary'
    _order = 'sequence'

    sequence = fields.Integer('Sequence')
    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    color = fields.Integer('Color Index')
    partner_position_ids = fields.One2many(
        'round.itinerary.position', 'itinerary_id', 'Partners')
    template_ids = fields.Many2many(
        'round.template',
        string='Vehicle')
    partner_ids = fields.Many2many('res.partner',
                                   string='Partners',
                                   compute='_compute_partner_ids',
                                   search='_search_partner_ids',
                                   readonly=True)

    @api.multi
    def _compute_partner_ids(self):
        for itinerary in self:
            partners = itinerary.mapped('partner_position_ids.partner_id')
            itinerary.partner_ids = [(6, 0, partners.ids)]

    def _search_partner_ids(self, operator, value):
        """
        Search for itinerary containing the customer name
        :param operator:
        :param value:
        :return:
        """

        partners = self.env['res.partner'].search([('name', operator, value)])
        positions = self.env['round.itinerary.position']\
            .search([('partner_id', 'in', partners.ids)])

        return [('partner_position_ids', 'in', positions.ids)]


class RoundItineraryPosition(models.Model):
    _name = 'round.itinerary.position'
    _order = 'sequence'

    itinerary_id = fields.Many2one(
        'round.itinerary', 'Itinerary',
        ondelete='cascade')
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        required=True,
        ondelete='restrict',
        domain=[('customer', '=', True)],
        index=True)
    partner_zip = fields.Char('Partner ZIP',
                              related='partner_id.zip',
                              readonly=True)
    partner_city = fields.Char('Partner city',
                               related='partner_id.city',
                               readonly=True)
    partner_street = fields.Char('Partner street',
                                 related='partner_id.street',
                                 readonly=True)
    tag_ids = fields.Many2many('round.tag', string='Tags')

    @api.multi
    @api.depends('itinerary_id')
    def name_get(self):
        result = []
        for rec in self:
            code = rec.itinerary_id.code
            result.append((rec.id, code))
        return result
