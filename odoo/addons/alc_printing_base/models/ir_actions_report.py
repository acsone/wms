# © 2017 Jacques-Etienne Baudoux <je@bcim.be>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import unicodedata

import lxml.html

from odoo import api

from odoo.addons.base_report_to_printer.models.ir_actions_report import (
    IrActionsReport as IrActionsReportBase,
)


class IrActionsReport(IrActionsReportBase):
    @api.model
    def _get_raw(self, oids, report_name, qty=1, **extra):
        report = self.env.ref(report_name)
        report_obj = report.env[report.model]
        docs = report_obj.browse(oids)
        docargs = {
            "doc_ids": oids,
            "doc_model": report.model,
            "docs": docs,
            "report": report,
            "qty": qty,
        }
        docargs.update(extra)
        template = report.report_name
        html = self._render_qweb_html(template, oids, docargs)[0]
        text = ""
        # pylint: disable=except-pass
        try:
            root = lxml.html.fromstring(html)
            match_klass = (
                "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"
            )
            for _x in range(qty):
                for node in root.xpath(match_klass.format("raw")):
                    text += node.text
        except lxml.etree.XMLSyntaxError:
            pass
        text = text.replace("\n", "")
        if not isinstance(text, str):
            text = text.decode("utf-8")
        nfkd_form = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
        text = text.encode("ASCII", "ignore")
        text = text.decode("unicode_escape")
        return text
