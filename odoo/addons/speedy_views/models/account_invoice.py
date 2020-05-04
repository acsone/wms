# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import api, fields, models

from .utils import create_index, install_trgm_extension


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    partner_id = fields.Many2one(index=True)

    @api.model_cr
    def init(self):
        trgm_installed = install_trgm_extension(self.env)
        self.env.cr.commit()

        if trgm_installed:
            index_name = "account_invoice_origin_gin_trgm"
            create_index(
                self.env.cr, index_name, self._table, "USING gin (origin gin_trgm_ops)"
            )

        # default list view sort by those fields desc
        index_name = "account_invoice_list_sort_index"
        create_index(
            self.env.cr,
            index_name,
            self._table,
            "(date_invoice desc, number desc, id desc) ",
        )
