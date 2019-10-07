# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof <svh@sylvainvh.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    picking_zone_id = fields.Many2one('picking.zone', string='Picking zone')
    zone = fields.Char('Zone')
    corridor = fields.Char('Corridor')
    shelf = fields.Char('Shelf')
    height = fields.Char('Height')
    box = fields.Char('Box')
    is_valid_location = fields.Boolean(
        'Valid location',
        compute='_compute_is_valid_location',
        store=True,
        readonly=True,
    )

    _sql_constraints = [
        (
            'unique_location_coordinates',
            'UNIQUE(zone, corridor, shelf, height, box)',
            _('The location coordinate must be unique'),
        )
    ]

    @api.multi
    @api.depends('zone', 'corridor', 'shelf', 'height', 'box')
    def _compute_is_valid_location(self):
        for location in self:
            if (
                not location.zone
                or not location.corridor
                or not location.shelf
                or not location.height
                or not location.box
            ):
                location.is_valid_location = False
            else:
                location.is_valid_location = True
                location.name = u'{}{}{}{}{}'.format(
                    location.zone,
                    location.corridor,
                    location.shelf,
                    location.height,
                    location.box,
                )

    @api.multi
    def name_get(self):
        """ Redefined from standard Odoo !

        By default when a location as the usage field set as 'view' its name
        is not computed with its parents location.
        Here we want the same to happen when a location as the flag
        'act_as_view' set.

        """
        ret_list = []
        for location in self:
            orig_location = location
            name = location.name
            # Chanded from default implementation
            # while location.location_id and location.usage != 'view':
            while (
                location.location_id
                and location.usage != 'view'
                and not location.act_as_view
            ):
                location = location.location_id
                name = location.name + "/" + name
            ret_list.append((orig_location.id, name))
        return ret_list
