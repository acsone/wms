# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.addons.component.core import Component


class IrAttachmentMapper(Component):
    _name = "esb.ir.attachment.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "ir.attachment"

    direct = [("datas_fname", "filename"), ("datas", "data")]


class IrAttachmentCronExporter(Component):
    _name = "esb.ir.attachment.cron.exporter"
    _inherit = "esb.cron.exporter"
    _usage = "record.exporter.cron"
    _apply_on = "ir.attachment"

    def get_items_domain(self):
        return [
            ("res_model", "in", ["stock.picking", "sale.order", "account.invoice"]),
            "|",
            ("name", "=like", "cf_%"),
            "|",
            ("name", "=like", "CM_%"),
            "|",
            ("name", "=like", "fc_%"),
            "|",
            ("name", "=like", "nc_%"),
            ("name", "=like", "NE_%"),
        ]

    def _get_producer(self):
        return self.work.component(usage="zip.producer")
