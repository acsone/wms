# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo.addons.account.models.ir_actions_report import (
    IrActionsReport as IrActionsReportBase,
)


class IrActionsReport(IrActionsReportBase):
    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        # Custom behavior for 'account.report_invoice'.
        if self._get_report(report_ref).report_name not in (
            "account.report_invoice",
            "account.report_invoice_with_payments",
        ):
            return super()._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=res_ids
            )

        invoices = self.env["account.move"].browse(res_ids)
        sorted_invoices = invoices.sorted(
            lambda i: (i.partner_id.name and i.partner_id.name.lower(), i.name)
        )
        collected_streams = OrderedDict()
        for invoice in sorted_invoices:
            steams = super()._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=invoice.ids
            )
            collected_streams[invoice.id] = steams.get(invoice.id)
        return collected_streams
