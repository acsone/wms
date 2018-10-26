# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def do_transfer(self):
        result = super(StockPicking, self).do_transfer()

        # magic word to skip create_draft_invoice
        if self.env.context.get('__no_job_create_draft_invoice'):
            return result

        picking_type_out = self.env.ref('stock.picking_type_out')
        out_picking = self.filtered(
            lambda picking: picking.picking_type_id == picking_type_out)
        if not out_picking:
            return result
        proc_group_ids = out_picking.mapped('move_lines.group_id').ids
        sales = self.env['sale.order'].search([
            ('procurement_group_id', 'in', proc_group_ids),
            ('invoice_status', '=', 'to invoice'),
            ('partner_invoice_id.invoice_grouping', '=', 'by_delivery')])
        if sales:
            sales.with_delay()._job_create_draft_invoice()
        return result
