# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ReportXmlPurchaseOrderUbl(models.AbstractModel):
    _name = "report.alc_purchase_order_ubl.report_xml_purchase_order_ubl"

    @api.multi
    def render_html(self, docids, data=None):
        purchase_order = self.env["purchase.order"].browse(docids)
        return purchase_order._generate_ubl_order_document()
