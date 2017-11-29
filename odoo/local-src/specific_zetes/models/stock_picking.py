# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import random

from odoo import models, fields, api, _
from odoo.exceptions import UserError

from .. import constants


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    operator_id = fields.Many2one(track_visibility='onchange')
    checksum = fields.Char('Checksum')
    zetes_state = fields.Selection([
        (constants.AS_DEFAULT, 'Default'),
        (constants.AS_START, 'Start'),
        (constants.AS_ACTIVE, 'Active'),
        (constants.AS_STAGING, 'Staging'),
        (constants.AS_DONE, 'Done'),
        (constants.AS_CANCELED, 'Canceled'),
        (constants.AS_FINISHED, 'Finished')
    ],
        string='Zetes state',
        default=constants.AS_DEFAULT,
        required=True)
    is_zetes_error = fields.Boolean('Zetes error', default=False)
    zetes_traceback = fields.Text('Zetes traceback')
    zetes_picking_type = fields.Selection([
        (constants.PICKING_ASSIGNMENT, 'Customer'),
        (constants.PARKING_ASSIGNMENT, 'Parking'),
        (constants.RESERVE_ASSIGNMENT, 'Reserve')],
        string="Picking type",
        default=constants.PICKING_ASSIGNMENT,
        required=True
    )

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
    def reset_picking(self):
        """
        Reset
        :return:
        """

        for picking in self:
            print

    @api.multi
    def interrupt_picking(self):
        self.assign_picking_checksum()
        self.write({
            'operator_id': None,
        })


class PackOperationReserveRel(models.Model):
    _name = 'pack.operation.reserve.rel'

    pack_operation_id = fields.Many2one('stock.pack.operation',
                                        string='Pack operation',
                                        required=True)
    reserve_location_id = fields.Many2one('stock.location',
                                          string='Reserve',
                                          required=True)
    lot_id = fields.Many2one('stock.production.lot',
                             string='Lot')


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    zetes_state = fields.Selection([
        (constants.OP_DEFAULT, 'Default'),
        (constants.OP_PICKED, 'Picked'),
        (constants.OP_SHORTPICKED, 'Shortpicked'),
        (constants.OP_SKIPPED, 'Skipped'),
        (constants.OP_CUT, 'Cut'),
        (constants.OP_CANCELED, 'Canceled / Full')
    ],
        string='Zetes state',
        default=constants.OP_DEFAULT,
        required=True)

    @api.multi
    def create_reserve_pack_operation(self, reserve_quantity, lot_id=None):
        self.ensure_one()

        quantity_available = self.product_qty - self.qty_done
        if reserve_quantity > quantity_available:
            raise UserError(
                _('You cannot split this pack operation because '
                  'the new quantity (%s) is geater than '
                  'the available quantity (%s)') %
                (reserve_quantity, quantity_available))

        reserve_rel_obj = self.env['pack.operation.reserve.rel']
        reserve_rel = reserve_rel_obj.search([
            ('pack_operation_id', '=', self.id),
            ('lot_id', '=', lot_id)
        ], limit=1, order="id DESC")
        if not reserve_rel:
            raise UserError(_('Reserve not found'))

        new_pack = self.copy({
            'qty_done': 0.0,
            'product_qty': reserve_quantity,
            'location_dest_id': reserve_rel.reserve_location_id.id,
        })

        if lot_id:
            if not self.pack_lot_ids:
                raise UserError(_('No pack operation found'))
            pack_lot = self.pack_lot_ids.filtered(
                lambda line: line.lot_id.id == lot_id)
            if not pack_lot:
                raise UserError(
                    _('No pack operation found with ID %s' % lot_id))

            lot_quantity_available = pack_lot.qty_todo - pack_lot.qty
            if reserve_quantity > lot_quantity_available:
                raise UserError(
                    _('You cannot split this pack operation lot because '
                      'the new quantity (%s) is greater than '
                      'the available quantity (%s)') %
                    (reserve_quantity, lot_quantity_available))

            pack_lot.copy({
                'operation_id': new_pack.id,
                'qty_todo': reserve_quantity,
                'qty': 0
            })

            pack_lot.write({
                'qty_todo': pack_lot.qty_todo - reserve_quantity
            })

        self.write({
            'product_qty': self.product_qty - reserve_quantity
        })

        return new_pack


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_portable_printer = fields.Boolean('Portable printer', default=False)
