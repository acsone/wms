# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons.queue_job.exception import FailedJobError
from odoo.addons.queue_job.job import job
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    date_order_short = fields.Date(compute="_compute_date_order_short")
    is_unique_invoice = fields.Boolean(
        "Unique invoice", help="Create an unique invoice for this sale order"
    )

    @api.depends("date_order")
    def _compute_date_order_short(self):
        for sale in self:
            if sale.date_order:
                sale.date_order_short = datetime.strptime(
                    sale.date_order, DEFAULT_SERVER_DATETIME_FORMAT
                ).date()

    @api.model
    def _cron_invoice_makeall(self, day):
        if day == -1:
            # take last day of current month (if run at end of the month)
            # of last day of previous month (if run at begin of next month)
            date = datetime.today()
            if date.day > 20:
                date += relativedelta(months=1)
            date = date.replace(day=1)
            date -= relativedelta(days=1)
            invoice_frequency = ["10_days", "1_month"]
        else:
            date = datetime.today()
            date = date.replace(day=day)
            invoice_frequency = ["10_days"]
        date_invoice = date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        query = """
        SELECT DISTINCT so.partner_invoice_id
        FROM sale_order AS so
          INNER JOIN res_partner AS partner
          ON partner.id = so.partner_invoice_id
        WHERE so.invoice_status = 'to invoice'
        AND partner.invoice_grouping = 'all_at_once'
        AND partner.invoice_frequency IN %s
        """
        self.env.cr.execute(query, (tuple(invoice_frequency),))
        partner_ids = [x[0] for x in self.env.cr.fetchall()]

        for partner_id in partner_ids:
            self.with_delay(priority=9)._job_invoices_by_partner(
                partner_id, date_invoice
            )

        query = """
        SELECT invoice.id
        FROM account_invoice AS invoice
          INNER JOIN res_partner AS partner
          ON invoice.partner_id = partner.id
        WHERE partner.invoice_grouping = 'by_delivery'
        AND partner.invoice_frequency IN %s
        AND invoice.state = 'draft'
        AND invoice.type in ('out_invoice', 'out_refund')
        """
        self.env.cr.execute(query, (tuple(invoice_frequency),))
        invoice_ids = [x[0] for x in self.env.cr.fetchall()]
        invoices = self.env["account.invoice"].browse(invoice_ids)
        for invoice in invoices:
            invoice.with_delay(priority=3)._job_validate_invoice(date_invoice)

    @api.multi
    @job(default_channel="root.background.invoice_creation")  # priority=9
    def _job_create_draft_invoice(self):
        self.with_context(mail_auto_subscribe_no_notify=True).action_invoice_create(
            final=True
        )

    @api.multi
    @job(default_channel="root.background.invoice_creation")  # priority=9
    def _job_invoices_by_partner(self, partner_id, date_invoice):
        partner = self.env["res.partner"].browse(partner_id)
        if partner.invoice_grouping != "all_at_once":
            raise FailedJobError("Invalid invoice grouping")

        invoice_ids = []
        # Create all the invoices
        to_invoice_sales = self.search(
            [
                ("invoice_status", "=", "to invoice"),
                ("partner_invoice_id", "=", partner.id),
                ("order_line.qty_to_invoice", ">", 0),
            ]
        )
        invoice_ids += to_invoice_sales.action_invoice_create(final=False)
        # Create all the refunds
        to_refund_sales = self.search(
            [
                ("invoice_status", "=", "to invoice"),
                ("partner_invoice_id", "=", partner.id),
                ("order_line.qty_to_invoice", "<", 0),
            ]
        )
        invoice_ids += to_refund_sales.action_invoice_create(final=True)
        invoices = self.env["account.invoice"].browse(invoice_ids)
        # Validate invoices
        invoices.with_delay(priority=3)._job_validate_invoice(date_invoice)

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """Overloaded to generate invoices all at once and separately based
        on the sale order configuration.
        """
        invoice_ids = []
        # Invoice all SO at once (standard behavior)
        sales_to_merge = self.search(
            [("id", "in", self.ids), ("is_unique_invoice", "=", False)]
        )
        sales_to_merge = sales_to_merge.with_context(mail_auto_subscribe_no_notify=True)
        if sales_to_merge:
            invoice_ids += super(SaleOrder, sales_to_merge).action_invoice_create(
                grouped, final
            )
        # Invoice SO separately
        sales_to_invoice = self.search(
            [("id", "in", self.ids), ("is_unique_invoice", "=", True)]
        )
        sales_to_invoice = sales_to_invoice.with_context(
            mail_auto_subscribe_no_notify=True
        )
        for sale_to_invoice in sales_to_invoice:
            invoice_ids += super(SaleOrder, sale_to_invoice).action_invoice_create(
                grouped, final
            )
        return invoice_ids
