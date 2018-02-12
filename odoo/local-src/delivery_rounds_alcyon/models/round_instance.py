# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)


class RoundInstance(models.Model):
    _inherit = 'round.instance'

    count_picking_available_total_ali = fields.Integer(
        'Picking Available Total Aliment',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total_ali = fields.Integer(
        'Picking Done Total Aliment',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_total_med = fields.Integer(
        'Picking Available Total Medicament',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total_med = fields.Integer(
        'Picking Done Total Medicament',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_total_frigo = fields.Integer(
        'Picking Available Total Frigo',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total_frigo = fields.Integer(
        'Picking Done Total Frigo',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_total_mat = fields.Integer(
        'Picking Available Total Materiel',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total_mat = fields.Integer(
        'Picking Done Total Materiel',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_total_pharm = fields.Integer(
        'Picking Available Total Pharmacie',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total_pharm = fields.Integer(
        'Picking Done Total Pharmacie',
        compute='_get_count_picking',
        readonly=True)

    @api.depends('picking_ids')
    def _get_count_picking(self):
        _logger.debug('_get_count_picking - start')
        keys = ('01', '02', '03', '04', '05')
        for rec in self:
            picking_total = {}.fromkeys(keys, 0)
            picking_done = {}.fromkeys(keys, 0)
            pickings = rec.picking_ids.filtered(
                lambda r: r.state in ('partially_available', 'assigned',
                                      'done'))
            for picking in pickings:
                key = picking.picking_type_id.picking_zone_id.code
                picking_total[key] += 1
                if picking.state == 'done':
                    picking_done[key] += 1

            rec.count_picking_available_total_med = picking_total.get('01', 0)
            rec.count_picking_available_total_mat = picking_total.get('02', 0)
            rec.count_picking_available_total_frigo = \
                picking_total.get('03', 0)
            rec.count_picking_available_total_ali = picking_total.get('04', 0)
            rec.count_picking_available_total_pharm = \
                picking_total.get('05', 0)

            rec.count_picking_done_total_med = picking_done.get('01', 0)
            rec.count_picking_done_total_mat = picking_done.get('02', 0)
            rec.count_picking_done_total_frigo = picking_done.get('03', 0)
            rec.count_picking_done_total_ali = picking_done.get('04', 0)
            rec.count_picking_done_total_pharm = picking_done.get('05', 0)

            rec.count_picking_available_total = sum(picking_total.values())
            rec.count_picking_done_total = sum(picking_done.values())

            rec.count_picking_available_partner = \
                len(pickings.mapped('partner_id'))
        _logger.debug('_get_count_picking - done')
