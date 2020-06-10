# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2016-2018 Camptocamp SA
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.addons.queue_job.job import job
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_unique_invoice = fields.Boolean(
        "Unique invoice",
        help="Create an unique invoice for this sale order",
        index=True,
    )

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
            invoice_frequencies = ["10_days", "1_month"]
        else:
            date = datetime.today()
            date = date.replace(day=day)
            invoice_frequencies = ["10_days"]
        date_invoice = date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # invoice the policy is resolved as follow: If grouping/frequency are
        # defined on the payment_mode, they are used otherwise we use the
        # information from the partner

        query = """
        SELECT
            so.partner_invoice_id,
            so.payment_mode_id
        FROM
            sale_order AS so
            INNER JOIN res_partner AS partner
                ON partner.id = so.partner_invoice_id
            LEFT JOIN account_payment_mode AS pm
                ON pm.id = so.payment_mode_id
        WHERE
            so.invoice_status = 'to invoice'
            AND COALESCE(pm.invoice_grouping, partner.invoice_grouping) = 'all_at_once'
            AND COALESCE(pm.invoice_frequency, partner.invoice_frequency) IN %s
        GROUP BY
            so.partner_invoice_id,
            so.payment_mode_id
        """
        cr = self.env.cr
        cr.execute(query, (tuple(invoice_frequencies),))
        for (partner_id, payment_mode_id) in cr.fetchall():
            self.with_delay(priority=9)._job_invoices_by_partner(
                partner_id, payment_mode_id, date_invoice
            )

        query = """
        SELECT
            invoice.id
        FROM
            account_invoice AS invoice
            INNER JOIN res_partner AS partner
                ON invoice.partner_id = partner.id
            LEFT JOIN account_payment_mode AS pm
                ON pm.id = invoice.payment_mode_id
        WHERE
            invoice.state = 'draft'
            AND invoice.type in ('out_invoice', 'out_refund')
            AND COALESCE(pm.invoice_grouping, partner.invoice_grouping) = 'by_delivery'
            AND COALESCE(pm.invoice_frequency, partner.invoice_frequency) IN %s
        """
        cr.execute(query, (tuple(invoice_frequencies),))
        invoice_ids = [x[0] for x in cr.fetchall()]
        invoices = self.env["account.invoice"].browse(invoice_ids)
        for invoice in invoices:
            invoice.with_delay(priority=3)._job_validate_invoice(date_invoice)

    @api.multi
    @job(default_channel="root.background.invoice_creation")  # priority=9
    def _job_invoices_by_partner(self, partner_id, payment_mode_id, date_invoice):
        invoice_ids = []
        with self._auto_join(["order_line"]):
            # When the left side of a domain leaf contains a dot ie
            # "order_line.qty_to_invoice", the orm will first query the
            # linked model (select id from sale_order_line where qty_to_invoice...)
            # and use the result into the query on the initial model with a in
            # operator. This process could lead to huge and inefficient queries
            # By using auto_join, we temporarily instruct the ORM that a SQL
            # join can be safely be used when building the SQL query in place
            # of the dummy mechanism. This is only safe if we are sure that no
            # record rule applies to the linked model

            # Create all the invoices
            to_invoice_sales = self.search(
                [
                    ("invoice_status", "=", "to invoice"),
                    ("partner_invoice_id", "=", partner_id),
                    ("order_line.qty_to_invoice", ">", 0),
                    ("payment_mode_id", "=", payment_mode_id),
                ]
            )
            invoice_ids += to_invoice_sales.action_invoice_create(final=False)
            # Create all the refunds
            to_refund_sales = self.search(
                [
                    ("invoice_status", "=", "to invoice"),
                    ("partner_invoice_id", "=", partner_id),
                    ("order_line.qty_to_invoice", "<", 0),
                    ("payment_mode_id", "=", payment_mode_id),
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
