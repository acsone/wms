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

    @api.multi
    def validate_picking(self):
        for picking in self:
            # The method "do_new_transfer" is the method called when
            # an user click on "Validate" on a picking.
            result = picking.do_new_transfer()

            # In Odoo this button will open a wizard in following case:
            # 1. A wizard if no quantity has been defined on lines
            #   (this wizard will set the quantity on each lines)
            # 2. A wizard if we need to create a back order
            if isinstance(result, dict):
                model = result.get('res_model')
                wizard = self.env[model].browse(int(result.get('res_id')))

                # Fortunately these wizards have the same
                # method "process" to execute the wizard
                wizard.process()


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
    def split_pack_op(self, new_qty, location_dest_id, lot_id=None):
        self.ensure_one()

        quantity_available = self.product_qty - self.qty_done
        if new_qty > quantity_available:
            raise UserError(
                _('You cannot split this pack operation because '
                  'the new quantity (%s) is geater than '
                  'the available quantity (%s)') %
                (new_qty, quantity_available))

        new_pack = self.copy({
            'qty_done': 0.0,
            'product_qty': new_qty,
            'location_dest_id': location_dest_id,
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
            if new_qty > lot_quantity_available:
                raise UserError(
                    _('You cannot split this pack operation lot because '
                      'the new quantity (%s) is greater than '
                      'the available quantity (%s)') %
                    (new_qty, lot_quantity_available))

            pack_lot.copy({
                'operation_id': new_pack.id,
                'qty_todo': new_qty,
                'qty': 0
            })

            pack_lot.write({
                'qty_todo': pack_lot.qty_todo - new_qty
            })

        self.write({
            'product_qty': self.product_qty - new_qty
        })

        return new_pack

    @api.multi
    def add_qty(self, qty, lot_id=None):
        """
        Add a qty on the pack operation
        :param qty: int - the qty to add
        :param lot_id: int - the ID of the lot
        :return:
        """
        self.ensure_one()

        self.qty_done += qty

        if not lot_id:
            return

        # When we have the lot, we will check if there no existing
        # quantity for this lot.
        pack_lot = \
            self.pack_lot_ids.filtered(lambda line: line.lot_id.id == lot_id)

        # If there no existing line (quantity) for this lot
        # we will create a new line
        if not len(pack_lot):
            self.pack_lot_ids.create({
                'operation_id': self.id,
                'qty': qty,
                'lot_id': lot_id,
            })
        # Otherwise we set the quantity for this lot
        # We don't need to add the new quantity to the lot
        # because Zetes send one request by lot
        else:
            pack_lot.write({'qty': qty})


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    is_portable_printer = fields.Boolean('Portable printer', default=False)
