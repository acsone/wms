# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from collections import OrderedDict

from odoo.addons.base.models import ir_actions_report


class IrActionsReport(ir_actions_report.IrActionsReport):
    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        batch_size = self._render_qweb_pdf_batch_size
        len_res_ids = len(res_ids) if res_ids else 0
        if (
            not res_ids
            or len_res_ids <= batch_size
            or not self._render_qweb_pdf_batch_enabled
        ):
            return super()._render_qweb_pdf_prepare_streams(report_ref, data, res_ids)
        collected_streams = OrderedDict()
        collected_false_streams = []
        for batch in self._split_batches(res_ids, batch_size=batch_size):
            new_collected_streams = super()._render_qweb_pdf_prepare_streams(
                report_ref, data, batch
            )
            for key, value in new_collected_streams.items():
                if key:
                    collected_streams[key] = value
                else:
                    collected_false_streams.append(value)
        streams_to_merge = [x["stream"] for x in collected_false_streams if x["stream"]]
        if streams_to_merge:
            if len(streams_to_merge) == 1:
                pdf_content_stream = streams_to_merge[0]
            else:
                pdf_content_stream = self._merge_pdfs(streams_to_merge)
            collected_streams[False] = {
                "stream": pdf_content_stream,
                "attachment": None,
            }
        return collected_streams

    def _split_batches(self, res_ids, batch_size=1000):
        # when we create batch we can't end with a batch of size 1
        # because when the prepare_streams is called with a single id
        # it will return the stream whith the id as key and not False
        # as it's the case when we have multiple ids
        # This is required to preserve the order of the streams in the final pdf
        last_id = None
        total_size = len(res_ids)
        if total_size <= batch_size:
            yield res_ids
            return
        if total_size % batch_size == 1:
            last_id = res_ids[-1]
            res_ids = res_ids[:-1]
            total_size -= 1
        for i in range(0, total_size, batch_size):
            if i == total_size - batch_size and last_id:
                yield res_ids[i : i + batch_size] + [last_id]
            else:
                yield res_ids[i : i + batch_size]

    @property
    def _render_qweb_pdf_batch_size(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_report_qweb_pdf_batch.render_qweb_pdf_batch_size")
        )

    @property
    def _render_qweb_pdf_batch_enabled(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("alc_report_qweb_pdf_batch.enable_render_qweb_pdf_batch")
        )
