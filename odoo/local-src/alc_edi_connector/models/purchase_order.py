# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    is_edi_available = fields.Boolean(
        related="partner_id.use_edi_connector", readonly=True
    )

    def send_ubl_order_document(self):
        self.ensure_one()
        self.partner_id.check_is_edi_supported()
        self.partner_id.alc_edi_connector_id.send_order_document(self)
