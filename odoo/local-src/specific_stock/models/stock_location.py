# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    picking_zone_id = fields.Many2one('picking.zone', string='Picking zone')
    zone = fields.Char('Zone')
    corridor = fields.Char('Corridor')
    shelf = fields.Char('Shelf')
    height = fields.Char('Height')
    box = fields.Char('Box')
    is_valid_location = fields.Boolean('Valid location',
                                       compute='_compute_is_valid_location',
                                       store=True,
                                       readonly=True)

    _sql_constraints = [('unique_location_coordinates',
                         'UNIQUE(zone, corridor, shelf, height, box)',
                         _('The location coordinate must be unique'))]

    @api.multi
    @api.depends('zone', 'corridor', 'shelf', 'height', 'box')
    def _compute_is_valid_location(self):
        for location in self:
            if not location.zone \
                    or not location.corridor \
                    or not location.shelf \
                    or not location.height \
                    or not location.box:
                location.is_valid_location = False
            else:
                location.is_valid_location = True
                location.name = '{}{}{}{}{}'.format(
                    location.zone,
                    location.corridor,
                    location.shelf,
                    location.height,
                    location.box)
