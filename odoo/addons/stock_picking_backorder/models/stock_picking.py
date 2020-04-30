# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_new_transfer(self):
        self.ensure_one()

        if self.picking_type_code == 'incoming':
            # At reception
            if (
                self.location_id.usage == 'supplier'
                and self.check_backorder()
                and not self.env.context.get('__no_backorder_choice')
            ):
                # From a PO (not a return) and backorder to make
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.backorder.choice',
                    'views': [[False, 'form']],
                    'context': {'default_picking_id': self.id},
                    'target': 'new',
                }
            else:
                return super(StockPicking, self).do_new_transfer()
        else:
            if self.check_backorder():
                # allow to process and create backorder even if no line
                # processed
                wiz = self.env['stock.backorder.confirmation'].create(
                    {'pick_id': self.id}
                )
                wiz.process()
            else:
                return super(StockPicking, self).do_new_transfer()

        return {}

    @api.multi
    def do_transfer(self):
        for pick in self:
            if (
                pick.state == 'draft'
                or all(x.qty_done == 0.0 for x in pick.pack_operation_ids)
            ) and pick.check_backorder():
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
