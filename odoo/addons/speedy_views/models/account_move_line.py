# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models

from .utils import create_index


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Reconciliation processes use intensive searches on those fields
    debit = fields.Monetary(index=True)
    credit = fields.Monetary(index=True)
    amount_residual = fields.Monetary(index=True)
    invoice_id = fields.Many2one(index=True)

    @api.model_cr
    def init(self):
        # in reconcile wizard, queries look for null or false values
        # for 'reconciled'. We improve the mass reconciliations with
        # this partial index
        index_name = "account_move_line_not_reconciled_index"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(reconciled) WHERE " "reconciled IS NULL OR NOT reconciled ",
        )

        # in reconcile wizard, a query is regularly issued with an
        # order by date_maturity, id, and we improve from 6s to 0.5ms
        index_name = "account_move_line_date_maturity_order_index"
        create_index(self.env.cr, index_name, self._table, "(date_maturity, id)")
