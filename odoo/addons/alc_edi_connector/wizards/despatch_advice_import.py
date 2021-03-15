# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, models

from odoo.addons.queue_job.job import job


class DespatchAdviceImport(models.TransientModel):
    _inherit = "despatch.advice.import"

    @job(default_channel="root.background.edi")
    def process_attachment(self, attachment):
        parsed_despatch_document = self.parse_despatch_advice(
            base64.b64decode(attachment.datas), attachment.name
        )
        self.process_data(parsed_despatch_document)

        # After process document -- attach DespatchAdvice to all
        lines = parsed_despatch_document.get("lines")

        body = _("DespatchAdvice received")
        title = _("Connector EDI")

        order_names = list({line["ref"] for line in lines})
        orders = self.env["purchase.order"].search([("name", "in", order_names)])

        for order in orders:
            attachment_out = self.env["ir.attachment"].search(
                [
                    ("name", "=", attachment.name),
                    ("res_id", "=", order.id),
                    ("res_model", "=", order._name),
                ]
            )
            if not attachment_out:
                attachment_out = self.env["ir.attachment"].create(
                    {
                        "name": attachment.name,
                        "res_id": order.id,
                        "res_model": order._name,
                        "datas": base64.b64encode(attachment.datas),
                        "datas_fname": attachment.name,
                    }
                )
                order.message_post(
                    body=body,
                    subject=title,
                    subtype="mt_note",
                    attachment_ids=attachment_out.ids,
                )
