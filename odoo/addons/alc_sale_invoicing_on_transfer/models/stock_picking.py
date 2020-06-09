# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.osv.expression import FALSE_LEAF


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _get_so_to_invoice_domain(self):
        picking_types = self.env["stock.picking.type"].search(
            [("create_invoice_on_transfer", "=", True)]
        )
        create_invoice_pickings = self.filtered(
            lambda picking: picking.picking_type_id in picking_types
        )
        if not create_invoice_pickings:
            return FALSE_LEAF
        proc_groups = create_invoice_pickings.mapped("move_lines.group_id")
        return [
            ("procurement_group_id", "in", proc_groups.ids),
            ("invoice_status", "=", "to invoice"),
        ]

    @api.multi
    def do_transfer(self):
        result = super(StockPicking, self).do_transfer()

        # magic word to skip create_draft_invoice
        if self.env.context.get("__no_job_create_draft_invoice"):
            return result

        so_domain = self._get_so_to_invoice_domain()
        if so_domain == FALSE_LEAF:
            return result
        sales = self.env["sale.order"].search(so_domain)
        if sales:
            sales.with_delay(priority=9)._job_create_draft_invoice()
        return result
