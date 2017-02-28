# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import date

from openerp import models, api, _
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT

DATE_LENGTH = len(date.today().strftime(DATE_FORMAT))


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def create_lots_for_picking(self):
        return super(StockPicking, self.with_context(
            default_life_date_allowed=True
        )).create_lots_for_picking()

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
