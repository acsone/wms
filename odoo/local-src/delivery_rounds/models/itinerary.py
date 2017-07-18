# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


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


class RoundItineraryPosition(models.Model):
    _name = 'round.itinerary.position'
    _rec_name = 'itinerary_id'
    _order = 'sequence'

    itinerary_id = fields.Many2one(
        'round.itinerary', 'Itinerary',
        ondelete='cascade')
    sequence = fields.Integer('Sequence')
    partner_id = fields.Many2one(
        'res.partner', 'Partner',
        required=True,
        ondelete='restrict',
        domain=[('customer', '=', True)])
