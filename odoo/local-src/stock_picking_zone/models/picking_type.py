# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    picking_zone_id = fields.Many2one('picking.zone', string='Picking zone')
