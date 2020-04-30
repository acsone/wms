# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    MONTHS = [
        ('01', 'January'),
        ('02', 'February'),
        ('03', 'March'),
        ('04', 'April'),
        ('05', 'May'),
        ('06', 'June'),
        ('07', 'July'),
        ('08', 'August'),
        ('09', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]

    invoice_month = fields.Selection(MONTHS, readonly=True)

    due_month = fields.Selection(MONTHS, readonly=True)

    def _select(self):
        res = super(AccountInvoiceReport, self)._select()
        # Add month value on select request for the sale report
        # Sale report is a report based on SQL request.
        return (
            res + ", TO_CHAR(sub.date, 'MM') as invoice_month"
            ", TO_CHAR(sub.date_due, 'MM') as due_month"
        )
