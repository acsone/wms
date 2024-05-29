# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from base64 import b64encode

from odoo import _, models


class AlcReportPrintAsync(models.AbstractModel):
    _name = "alc.report.print.async"
    _description = "job queued report"

    def get_report_name(self):
        raise NotImplementedError

    def print_and_attach_report(self, report, send_to_fax=None):
        """Print and attach a report.

        param send_to_fax: If not empty the attachment will be sent
        to the number specified.
        """
        self.ensure_one()
        filename = self.get_report_name()
        data = self.env["ir.actions.report"]._render_qweb_pdf(report, [self.id])[0]
        existing = self.env["ir.attachment"].search(
            [("name", "=", filename), ("res_model", "=", self._name)]
        )
        if len(existing) > 0:
            existing[0].datas = b64encode(data)
        else:
            new_report = self.env["ir.attachment"].create(
                {
                    "type": "binary",
                    "res_model": self._name,
                    "res_id": self.id,
                    "name": filename,
                    "mimetype": "application/pdf",
                    "datas": b64encode(data),
                }
            )
        if send_to_fax:
            report_id = existing[0].id if len(existing) > 0 else new_report.id
            fax = self.env.ref("alc_external_fax.ovh")
            fax.with_delay(
                description=_("Sending fax for %(obj)s with id %(objid)s").format(
                    obj=self._name, objid=self.id
                ),
                priority=10,
            ).send(send_to_fax, report_id)
