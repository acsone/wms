# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import models, api, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

DATE_LENGTH = len(date.today().strftime(DATE_FORMAT))


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def _create_lots_for_picking(self):
        return super(StockPicking, self.with_context(
            default_life_date_allowed=True
        ))._create_lots_for_picking()

    @api.multi
    def do_new_transfer(self):
        result = super(StockPicking, self).do_new_transfer()

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

        return result

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

        original_picking_type_id = self.mapped('picking_type_id')
        if len(original_picking_type_id) == 1:
            packages = \
                self.mapped('pack_operation_ids.result_package_id')\
                .filtered(lambda package: not package.original_picking_type_id)
            packages.write({
                'original_picking_type_id': original_picking_type_id.id,
            })

        return result
