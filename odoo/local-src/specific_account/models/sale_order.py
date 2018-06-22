# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, registry, _
from odoo.addons.queue_job.job import job
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,\
    DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_order_short = fields.Date(compute='_compute_date_order_short')
    is_unique_invoice = fields.Boolean(
        'Unique invoice',
        help='Create an unique invoice for this sale order')

    @api.depends('date_order')
    def _compute_date_order_short(self):
        for sale in self:
            if sale.date_order:
                sale.date_order_short = datetime.strptime(
                    sale.date_order, DEFAULT_SERVER_DATETIME_FORMAT
                ).date()

    @api.model
    def _cron_invoice_makeall(self, day):
        chunk_size = \
            self.env['ir.config_parameter'].get_param('account.chunk_size', 0)
        chunk_size = int(chunk_size)
        if not chunk_size:
            raise UserError(_('Please set the chunk size in account settings'))

        if day == -1:
            # take last day of current month (if run at end of the month)
            # of last day of previous month (if run at begin of next month)
            date = datetime.today()
            if date.day > 20:
                date += relativedelta(months=1)
            date = date.replace(day=1)
            date -= relativedelta(days=1)
            invoice_frequency = ['10_days', '1_month']
        else:
            date = datetime.today()
            date = date.replace(day=day)
            invoice_frequency = ['10_days']
        date_invoice = date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        query = """
        SELECT DISTINCT so.partner_id
        FROM sale_order AS so
          INNER JOIN res_partner AS partner ON partner.id = so.partner_id
        WHERE so.invoice_status = 'to invoice'
        AND partner.invoice_grouping = 'all_at_once'
        AND partner.invoice_frequency IN %s
        UNION ALL
        SELECT DISTINCT invoice.partner_id
        FROM account_invoice AS invoice
          INNER JOIN res_partner AS partner ON invoice.partner_id = partner.id
        WHERE partner.invoice_grouping = 'by_delivery'
        AND partner.invoice_frequency IN %s
        AND invoice.state = 'draft'
        """
        self.env.cr.execute(query, (tuple(invoice_frequency),
                                    tuple(invoice_frequency)))
        partner_ids = [x[0] for x in self.env.cr.fetchall()]

        index = 0
        while index < len(partner_ids):
            chunk = partner_ids[index: index + chunk_size]
            self.with_delay()._job_invoices_by_partners(chunk, date_invoice)
            index += chunk_size

    @api.multi
    @job(default_channel='root.invoices_creation')
    def _job_create_draft_invoice(self):

        self.with_context(mail_auto_subscribe_no_notify=True)\
            .action_invoice_create(final=True)

    @api.multi
    @job(default_channel='root.invoices_creation')
    def _job_invoices_by_partners(self, partner_ids, date_invoice):
        for partner in self.env['res.partner'].browse(partner_ids):
            try:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))
                AccountInvoice = self.env['account.invoice']

                invoice_grouping = partner.invoice_grouping

                if not invoice_grouping:
                    continue

                if invoice_grouping == 'all_at_once':
                    sales_to_merge = self.search(
                        [('invoice_status', '=', 'to invoice'),
                         ('partner_id', 'in', partner_ids),
                         ('is_unique_invoice', '=', False)])
                    sales_to_merge = sales_to_merge\
                        .with_context(mail_auto_subscribe_no_notify=True)
                    invoice_ids = \
                        sales_to_merge.action_invoice_create(final=True)
                    invoices = AccountInvoice.browse(invoice_ids)
                elif invoice_grouping == 'by_delivery':
                    invoices = AccountInvoice.search([
                        ('partner_id', '=', partner.id),
                        ('state', '=', 'draft')
                    ])
                else:
                    raise UserError(_('Unknown invoice type'))

                sales_to_invoice = self.search(
                    [('invoice_status', '=', 'to invoice'),
                     ('partner_id', 'in', partner_ids),
                     ('is_unique_invoice', '=', True)])

                invoice_ids = []
                for sale_to_invoice in sales_to_invoice:
                    invoice_ids.append(
                        sale_to_invoice.action_invoice_create(final=True))

                if invoice_ids:
                    invoices |= AccountInvoice.browse(invoice_ids)

                cr.commit()

                # Set date
                invoices.write({
                    'date_invoice': date_invoice})
                cr.commit()

                # Validate invoices
                invoices.action_invoice_open()
                cr.commit()
            except Exception as e:
                _logger.error(
                    "Invoice Generation Cron Error with partner %s: %s" %
                    (partner.id, e))
            finally:
                try:
                    cr.close()
                except Exception:
                    pass
