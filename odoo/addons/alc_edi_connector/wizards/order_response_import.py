# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import models
from odoo.addons.queue_job.job import job


class OrderResponseImport(models.TransientModel):
    _inherit = "order.response.import"

    @job(default_channel='root.background.edi')
    def process_attachment(self, attachment):
        parsed_order_document = self.parse_order_response(
            base64.b64decode(attachment.datas), attachment.name
        )
        self.process_data(parsed_order_document)
