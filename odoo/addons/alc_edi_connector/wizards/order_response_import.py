# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.job import job


class OrderResponseImport(models.TransientModel):
    _inherit = "order.response.import"

    @job(default_channel="root.background.edi")
    def process_attachment(self, attachment):
        parsed_order_document = self.parse_order_response(
            base64.b64decode(attachment.datas), attachment.name
        )

        po_name = parsed_order_document.get("ref")
        order = self.env["purchase.order"].search([("name", "=", po_name)])
        if not order:
            raise ValidationError(_("No purchase order found for name %s.") % po_name)

        # PO is already validated by an order response
        if order.state == "purchase":
            body = _(
                "UBL Order document already received. This next one will not be taken into account"
            )
            title = _("Connector EDI")
            attachment = self.env["ir.attachment"].create(
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
                attachment_ids=attachment.ids,
            )

            return _(
                "Purchase Order has already been modified by a previous Order response."
            )
        self.process_data(parsed_order_document)
        return ""
