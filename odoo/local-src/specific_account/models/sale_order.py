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
        """
        self.env.cr.execute(query, (tuple(invoice_frequency), ))
        partner_ids = [x[0] for x in self.env.cr.fetchall()]

        index = 0
        while index < len(partner_ids):
            chunk = partner_ids[index: index + chunk_size]
            self.with_delay()._job_invoices_by_partners(chunk, date_invoice)
            index += chunk_size

        query = """
        SELECT invoice.id
        FROM account_invoice AS invoice
          INNER JOIN res_partner AS partner ON invoice.partner_id = partner.id
        WHERE partner.invoice_grouping = 'by_delivery'
        AND partner.invoice_frequency IN %s
        AND invoice.state = 'draft'
        AND invoice.type = 'out_invoice'
        """
        self.env.cr.execute(query, (tuple(invoice_frequency), ))
        invoice_ids = [x[0] for x in self.env.cr.fetchall()]
        invoices = self.env['account.invoice'].browse(invoice_ids)
        for invoice in invoices:
            invoice.with_delay()._job_validate_invoice(date_invoice)

    @api.multi
    @job(default_channel='root.invoice_creation')
    def _job_create_draft_invoice(self):
        self.with_context(mail_auto_subscribe_no_notify=True)\
            .action_invoice_create(final=True)

    @api.multi
    @job(default_channel='root.invoice_creation')
    def _job_invoices_by_partners(self, partner_ids, date_invoice):
        partners = self.env['res.partner'].browse(partner_ids)
        assert all(p.invoice_grouping == 'all_at_once' for p in partners), \
            "Invalid invoice grouping"
        for partner in partners:
            try:
                cr = registry(self._cr.dbname).cursor()
                self = self.with_env(self.env(cr=cr))

                sales_to_merge = self.search(
                    [('invoice_status', '=', 'to invoice'),
                        ('partner_id', '=', partner.id),
                        ('is_unique_invoice', '=', False)])
                sales_to_merge = sales_to_merge\
                    .with_context(mail_auto_subscribe_no_notify=True)
                invoice_ids = \
                    sales_to_merge.action_invoice_create(final=True)

                sales_to_invoice = self.search([
                    ('invoice_status', '=', 'to invoice'),
                    ('partner_id', '=', partner.id),
                    ('is_unique_invoice', '=', True)])
                sales_to_invoice = sales_to_invoice\
                    .with_context(mail_auto_subscribe_no_notify=True)
                for sale_to_invoice in sales_to_invoice:
                    invoice_ids.append(
                        sale_to_invoice.action_invoice_create(final=True))

                invoices = self.env['account.invoice'].browse(invoice_ids)

                # Validate invoices
                invoices.with_delay()._job_validate_invoice(date_invoice)
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
