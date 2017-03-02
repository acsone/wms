# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    zone = fields.Char('Zone')
    corridor = fields.Char('Corridor')
    shelf = fields.Char('Shelf')
    height = fields.Char('Height')
    box = fields.Char('Box')
    is_valid_location = fields.Boolean('Valid location',
                                       compute='_compute_is_valid_location')

    @api.multi
    @api.constrains('zone', 'corridor', 'shelf', 'height', 'box')
    @api.onchange('zone', 'corridor', 'shelf', 'height', 'box')
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
                location.name = '{}{}{}{}'.format(location.corridor,
                                                  location.shelf,
                                                  location.height,
                                                  location.box)
