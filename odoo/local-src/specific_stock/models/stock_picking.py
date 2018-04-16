# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import models, api, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.exceptions import UserError

DATE_LENGTH = len(date.today().strftime(DATE_FORMAT))


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    @api.multi
    def name_get(self):
        """ Display 'Warehouse code: PickingType_name' """
        res = []
        for picking_type in self:
            if picking_type.warehouse_id:
                name = '%s: %s' % (
                    picking_type.warehouse_id.code,
                    picking_type.name)
            else:
                name = picking_type.name
            res.append((picking_type.id, name))
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _create_lots_for_picking(self):
        return super(StockPicking, self.with_context(
            default_life_date_allowed=True
        ))._create_lots_for_picking()

    @api.multi
    def check_removal_date_on_transfer(self):

        for picking in self:
            bad_lots = []
            stock_op_lots = \
                picking.pack_operation_ids.mapped('pack_lot_ids')
            for line in stock_op_lots:
                if line.is_removal_date_expired \
                        and not picking.to_process_quant_expired:
                    bad_lots.append('%s (%s)' %
                                    (line.lot_id.name,
                                     line.lot_id.removal_date[:DATE_LENGTH]))
            if bad_lots:
                raise Warning(_('You cannot transfer lots with an expired '
                                'removal date:\n\t- %s' %
                                ('\n\t- '.join(bad_lots))))

    @api.multi
    def do_new_transfer(self):
        self.ensure_one()

        if (self.picking_type_code == 'incoming' and not self.grn_id):
            if (not self.env.context.get('__no_pick_receive_note_check') and
                    not self.env.context.get('test_mode')):
                raise UserError(_(
                    'The reception must be linked to a Goods Received Note'))

        result = {}

        if self.picking_type_code == 'incoming':
            # At reception
            if self.location_id.usage == 'customer' and self.check_backorder():
                # From a PO (not a return) and backorder to make
                wiz = self.env['stock.backorder.confirmation'].create({
                    'pick_id': self.id})
                if not self.partner_id.is_purchase_back_order_accepted:
                    wiz.process_cancel_backorder()
                else:
                    wiz.process()
                    # Ticket to create for missing products?
            else:
                result = super(StockPicking, self).do_new_transfer()
        else:
            if self.check_backorder():
                # allow to process and create backorder even if no line
                # processed
                wiz = self.env['stock.backorder.confirmation'].create({
                    'pick_id': self.id})
                wiz.process()
            else:
                result = super(StockPicking, self).do_new_transfer()

        if not self.env.context.get('__no_specific_stock_backorder'):
            self.check_removal_date_on_transfer()

        return result

    @api.multi
    def do_transfer(self):
        for pick in self:
            if ((pick.state == 'draft' or all([
                    x.qty_done == 0.0 for x in pick.pack_operation_ids])) and
                    pick.check_backorder()):
                # allow to transfer and create backorder even if no line
                # processed
                pick._create_backorder()
            else:
                super(StockPicking, self).do_transfer()
        return True

    @api.one
    def _compute_state(self):
        # Mark as done picking transfered without any line
        if not self.move_lines and self.printed:
            self.state = 'done'
        else:
            super(StockPicking, self)._compute_state()

    @api.multi
    @api.constrains('printed')
    def _propagate_printed(self):
        # When a picking is printed, it cannot be completed
        # anymore (see module stock_groupbypartner).
        # We need to propagate this rule to all pickings of the delivery round.
        if 'stop_propagate_printed' not in self.env.context:
            self.filtered('printed')\
                .mapped('delivery_round_id.picking_ids')\
                .with_context(stop_propagate_printed=True)\
                .write({'printed': True})

    @api.multi
    def put_in_pack(self):
        result = super(StockPicking, self).put_in_pack()

        original_picking_zone_id = \
            self.mapped('picking_type_id.picking_zone_id')
        if len(original_picking_zone_id) == 1:
            packages = \
                self.mapped('pack_operation_ids.result_package_id')\
                .filtered(lambda package: not package.original_picking_zone_id)
            packages.write({
                'original_picking_zone_id': original_picking_zone_id.id,
            })

        return result
