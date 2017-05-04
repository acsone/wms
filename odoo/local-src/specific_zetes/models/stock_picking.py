# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import random

from odoo import models, fields, api, _

# Zetes values for assignment (stock.picking) state
AS_DEFAULT = '00'
AS_START = '01'
AS_ACTIVE = '02'
AS_STAGING = '03'
AS_DONE = '04'
AS_CANCELED = '05'
AS_FINISHED = '08'

# Zetes values for picking (stock.pack.operation) state
OP_DEFAULT = '00'
OP_PICKED = '01'
OP_SHORTPICKED = '02'
OP_SKIPPED = '03'
OP_CUT = '04'
OP_CANCELED = '05'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operator_id = fields.Many2one(track_visibility='onchange')
    checksum = fields.Char('Checksum')
    zetes_state = fields.Selection([
        (AS_DEFAULT, 'Default'),
        (AS_START, 'Start'),
        (AS_ACTIVE, 'Active'),
        (AS_STAGING, 'Staging'),
        (AS_DONE, 'Done'),
        (AS_CANCELED, 'Canceled'),
        (AS_FINISHED, 'Finished')
    ],
        string='Zetes state',
        default=AS_DEFAULT,
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
        (OP_DEFAULT, 'Default'),
        (OP_PICKED, 'Picked'),
        (OP_SHORTPICKED, 'Shortpicked'),
        (OP_SKIPPED, 'Skipped'),
        (OP_CUT, 'Cut'),
        (OP_CANCELED, 'Canceled')
    ],
        string='Zetes state',
        default=OP_CANCELED,
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
