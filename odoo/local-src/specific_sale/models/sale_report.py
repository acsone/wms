# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class SaleReport(models.Model):
    _inherit = 'sale.report'

    month = fields.Selection(
        [
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
            ('12', 'December')
        ],
        readonly=True,
    )

    def _select(self):
        res = super(SaleReport, self)._select()
        # Add month value on select request for the sale report
        # Sale report is a report based on SQL request.
        return res + ", TO_CHAR(s.date_order, 'MM') as month"
