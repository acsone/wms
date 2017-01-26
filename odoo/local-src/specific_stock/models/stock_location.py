# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class StockLocation(models.Model):
    _inherit = 'stock.location'

    zone = fields.Char('Zone')
    corridor = fields.Char('Corridor')
    shelve = fields.Char('Shelve')
    height = fields.Char('Height')
    box = fields.Char('Box')
    is_valid_location = fields.Boolean('Valid location',
                                       compute='_compute_is_valid_location')

    @api.multi
    def _compute_is_valid_location(self):
        for location in self:
            if not location.zone \
                    or not location.corridor \
                    or not location.shelve \
                    or not location.height \
                    or not location.box:
                location.is_valid_location = False
            else:
                location.is_valid_location = True
