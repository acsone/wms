# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import random

from odoo import models, fields, api, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operator_id = fields.Many2one(track_visibility='onchange')
    checksum = fields.Char('Checksum')
    zetes_state = fields.Selection([
        ('00', 'Default'),
        ('01', 'Start'),
        ('02', 'Active'),
        ('03', 'Staging'),
        ('04', 'Done'),
        ('05', 'Cancelled'),
        ('08', 'Finished')
    ],
        string='Zetes state',
        default='00',
        required=True)
    is_zetes_error = fields.Boolean('Zetes error', default=False)
    zetes_traceback = fields.Text('Zetes traceback')

    @api.multi
    def assign_picking_checksum(self):
        active_picking_query = """
        SELECT checksum
        FROM stock_picking
        WHERE checksum IS NOT NULL
        AND state IN ('assigned', 'partially_available')
        """
        self.env.cr.execute(active_picking_query)
        active_picking_checksum = set([row[0]
                                       for row
                                       in self.env.cr.fetchall()])
        picking_checksums = set([format(i, '0%d' % 2)
                                 for i
                                 in range(1, 100)])

        checksum_available = picking_checksums - active_picking_checksum
        if not checksum_available:
            raise Warning('There is no picking checksum available')

        for picking in self:
            if picking.checksum:
                continue

            checksum = random.choice(list(checksum_available))
            checksum_available.remove(checksum)
            picking.checksum = checksum

    @api.multi
    def interrupt_picking(self):
        self.assign_picking_checksum()
        self.write({
            'operator_id': None,
        })


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    zetes_state = fields.Selection([
        ('00', 'Default'),
        ('01', 'Picked'),
        ('02', 'Shortpicked'),
        ('03', 'Skipped'),
        ('04', 'Cut'),
        ('05', 'Cancel')
    ],
        string='Zetes state',
        default='00',
        required=True)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    zone_code = fields.Char('Zone code')

    _sql_constraints = [
        (
            'unique_zone_code',
            'unique(zone_code)',
            _('The zone picking type code should be unique.')
        ),
    ]
