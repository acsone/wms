# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RoundTemplate(models.Model):
    _name = "round.template"
    _order = "time_leave_planned"

    name = fields.Char('Name')
    itinerary_ids = fields.Many2many(
        'round.itinerary',
        string="Itineraries")
    color = fields.Integer('Color Index')
    time_picking_planned = fields.Float(
        'Planned Picking Start Time')
    time_leave_planned = fields.Float(
        'Planned Vehicle Start Time')
