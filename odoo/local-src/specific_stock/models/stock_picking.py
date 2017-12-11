# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import models, api, _, fields
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
from odoo.exceptions import UserError

DATE_LENGTH = len(date.today().strftime(DATE_FORMAT))


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    picking_zone_id = fields.Many2one('picking.zone', string='Picking zone')

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
    def do_new_transfer_with_back_order(self, result):
        self.ensure_one()

        # In this case, we don't have back order
        # => we can ignore back order variants

        if not result or result['res_model'] != 'stock.backorder.confirmation':
            return result

        # Case: Purchase back order
        if self.picking_type_code == 'incoming':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'stock.backorder.choice',
                'views': [[False, 'form']],
                'context': {
                    'default_picking_id': self.id,
                    'default_backorder_confirmation_id': result['res_id'],
                },
                'target': 'new',
            }

        # Other cases
        else:
            return result

    @api.multi
    def do_new_transfer(self):
        self.ensure_one()

        if (self.picking_type_code == 'incoming' and not self.grn_id):
            raise UserError(_(
                'The reception must be linked to a Goods Received Note'))

        pick = self
        if ((pick.state == 'draft' or all([x.qty_done == 0.0 for x
                                           in pick.pack_operation_ids])) and
                pick.check_backorder()):
            # allow to receive and create backorder even if no line processed
            view = self.env.ref('stock.view_backorder_confirmation')
            wiz = self.env['stock.backorder.confirmation'].create({
                'pick_id': pick.id})
            result = {
                'name': _('Create Backorder?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.backorder.confirmation',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }
        else:
            result = super(StockPicking, self).do_new_transfer()

        result = self.do_new_transfer_with_back_order(result)

        self.check_removal_date_on_transfer()

        return result

    @api.multi
    def do_transfer(self):
        for pick in self:
            if ((pick.state == 'draft' or all([
                    x.qty_done == 0.0 for x in pick.pack_operation_ids])) and
                    pick.check_backorder()):
                # allow to receive and create backorder even if no line
                # processed
                pick._create_backorder()
            else:
                super(StockPicking, self).do_transfer()
        return True

    @api.depends('move_type', 'launch_pack_operations', 'move_lines.state',
                 'move_lines.picking_id', 'move_lines.partially_available')
    @api.one
    def _compute_state(self):
        if not self.move_lines and self.grn_id:
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
