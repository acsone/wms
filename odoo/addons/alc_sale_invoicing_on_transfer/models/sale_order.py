# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    @job(default_channel="root.background.invoice_creation")  # priority=9
    def _job_create_draft_invoice(self):
        to_invoice = self.filtered(lambda s: s.invoice_status == "to invoice")
        if not to_invoice:
            return "Invoices already created"
        return to_invoice.with_context(
            mail_auto_subscribe_no_notify=True
        ).action_invoice_create(final=True)
