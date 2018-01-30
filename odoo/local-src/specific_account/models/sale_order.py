# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, registry
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    date_order_short = fields.Date(compute='_compute_date_order_short')

    @api.depends('date_order')
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
        else:
            date = datetime.today()
            date = date.replace(day=day)

        try:
            cr = registry(self._cr.dbname).cursor()
            self = self.with_env(self.env(cr=cr))
            sales = self.search([('invoice_status', '=', 'to invoice')])
            # final: refund will be generated if necessary
            sales = sales.with_context(mail_auto_subscribe_no_notify=True)
            invoice_ids = sales.action_invoice_create(final=True)
            invoices = self.env['account.invoice'].browse(invoice_ids)
            cr.commit()

            # Set date
            invoices.write({
                'date_invoice': date.strftime(DEFAULT_SERVER_DATE_FORMAT)})
            cr.commit()

            # Validate invoices
            invoices.action_invoice_open()
            cr.commit()
        except Exception as e:
            _logger.error("Invoice Generation Cron Error: %s" % e)
        finally:
            try:
                cr.close()
            except Exception:
                pass
