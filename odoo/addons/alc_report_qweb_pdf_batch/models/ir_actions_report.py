# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import OrderedDict

from odoo.addons.base.models import ir_actions_report


class IrActionsReport(ir_actions_report.IrActionsReport):
    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        if not res_ids:
            return super().__render_qweb_pdf_prepare_streams(report_ref, data, res_ids)
        collected_streams = OrderedDict()
        batch_size = self._render_qweb_pdf_batch_size
        for batch in self._split_batches(res_ids, batch_size=batch_size):
            collected_streams.update(
                super()._render_qweb_pdf_prepare_streams(report_ref, data, batch)
            )
        return collected_streams

    def _split_batches(self, res_ids, batch_size=1000):
        for i in range(0, len(res_ids), batch_size):
            yield res_ids[i : i + batch_size]

    @property
    def _render_qweb_pdf_batch_size(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_report_qweb_pdf_batch.render_qweb_pdf_batch_size")
        )
