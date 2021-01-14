# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.queue_job.job import job, related_action


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @job(default_channel="root.background.invoice_validation")  # priority=3
    @related_action(action="related_action_open_invoice")
    def _job_validate_invoice(self, date_invoice):
        # Reload self as an invoice could have been deleted inbetween
        self = self.search([("id", "in", self.ids)])
        if not self:
            return
        # Set date
        self.write({"date_invoice": date_invoice})
        # Validate invoice
        self.action_invoice_open()
