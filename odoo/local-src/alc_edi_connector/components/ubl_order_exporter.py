# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _
from odoo.addons.component.core import Component


class UblOrderOrderExporter(Component):
    """ Synchronizer for importing data from a backend to Odoo """

    _name = 'ubl.order.exporter'
    _inherit = ['edi.exporter']
    _apply_on = 'purchase.order'
    _usage = 'ubl.order.exporter'

    def execute(self, purchase_order):
        xml_content = purchase_order.generate_ubl_xml_string(
            "order", version="2.2"
        )

        self.work._propagate_kwargs.append("record")
        setattr(self.work, "record", purchase_order)

        self.backend_adapter.push(xml_content)

        task_def = self.work.task_def
        attachment_name = task_def.filename(purchase_order)
        body = _("UBL Order document sent")
        title = _("Connector EDI")
        attachment = self.env['ir.attachment'].create(
            {
                'name': attachment_name,
                'res_id': purchase_order.id,
                'res_model': purchase_order._name,
                'datas': base64.b64encode(xml_content),
                'datas_fname': attachment_name,
            }
        )
        purchase_order.message_post(
            body=body,
            subject=title,
            subtype="mt_note",
            attachment_ids=attachment.ids,
        )
