# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime

from odoo import fields
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

        attachment_name = (
            "UblOrderDocument_%s.xml"
            % fields.Datetime.to_string(
                fields.Datetime.context_timestamp(
                    purchase_order, datetime.now()
                )
            )
        )
        self.env['ir.attachment'].create(
            {
                'name': attachment_name,
                'res_id': purchase_order.id,
                'res_model': purchase_order._name,
                'datas': base64.b64encode(xml_content),
                'datas_fname': attachment_name,
            }
        )
