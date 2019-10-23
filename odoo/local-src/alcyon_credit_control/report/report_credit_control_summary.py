# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class CreditControlSummaryReport(models.AbstractModel):
    _name = 'report.account_credit_control.report_credit_control_summary'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report_name = 'account_credit_control.report_credit_control_summary'
        report = report_obj._get_report_from_name(report_name)
        wizard = self.env['credit.control.communication']
        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': self.env[report.model].browse(docids),
            'data': data,
            'get_consolidate_lines': wizard.get_consolidate_lines,
        }
        return report_obj.render(report_name, docargs)
