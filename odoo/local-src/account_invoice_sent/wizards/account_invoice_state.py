# -*- coding: utf-8 -*-
# Copyright 2015-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _


class AccountInvoiceSent(models.TransientModel):
    """
    This wizard will mark as sent the all the selected validated invoices
    """
    _name = "account.invoice.sent"

    count_print = fields.Integer('To print', readonly=True)
    count_email = fields.Integer('By email', readonly=True)
    count_email_missing = fields.Integer(
        'Email address missing', readonly=True)

    email_copy = fields.Boolean(
        'Send copy by email',
        help="For printed documents",
        default=False)

    @api.model
    def default_get(self, fields_list):
        defaults = super(AccountInvoiceSent, self).default_get(fields_list)
        active_ids = self._context.get('active_ids', [])
        if active_ids is None:
            return {}
        invoices = self.env['account.invoice'].browse(active_ids).filtered(
            lambda r: (
                not r.sent and
                r.state not in ('draft', 'proforma', 'proforma2')))
        defaults['count_print'] = len(invoices.filtered(
            lambda r:
            r.partner_id.commercial_partner_id.invoice_sending_method ==
            'letter'))
        invoices_email = invoices.filtered(
            lambda r:
            r.partner_id.commercial_partner_id.invoice_sending_method ==
            'email')
        defaults['count_email'] = len(invoices_email)
        defaults['count_email_missing'] = (
            len(invoices_email) -
            len(invoices_email.filtered(
                "partner_id.commercial_partner_id.email")))
        return defaults

    @api.multi
    def button_print(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        active_ids = self._context.get('active_ids', [])
        if active_ids is None:
            return act_close
        invoices = self.env['account.invoice'].browse(active_ids).filtered(
            lambda r: (
                not r.sent and
                r.state not in ('draft', 'proforma', 'proforma2')))
        invoices = invoices.filtered(
            lambda r:
            r.partner_id.commercial_partner_id.invoice_sending_method ==
            'letter')
        if invoices:
            template = self.env.ref('account.email_template_edi_invoice')
            invoices.write({'sent': True})
            for invoice in invoices:
                invoice.message_post(body=_("Invoice sent"))
                if self.email_copy:
                    template.send_mail(invoice.id)
            res = self.env['report'].get_action(self, 'account.report_invoice')
            res['context']['active_ids'] = invoices.ids
            return res
        return act_close

    @api.multi
    def button_email(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        active_ids = self._context.get('active_ids', [])
        if active_ids is None:
            return act_close
        invoices = self.env['account.invoice'].browse(active_ids).filtered(
            lambda r: (
                not r.sent and
                r.state not in ('draft', 'proforma', 'proforma2')))
        invoices = invoices.filtered(
            lambda r:
            r.partner_id.commercial_partner_id.email and
            r.partner_id.commercial_partner_id.invoice_sending_method ==
            'email')
        if invoices:
            invoices.write({'sent': True})
            template = self.env.ref('account.email_template_edi_invoice')
            for invoice in invoices:
                invoice.message_post(body=_("Invoice sent"))
                template.send_mail(invoice.id)
        return act_close

    @api.multi
    def button_mark_only(self):
        act_close = {'type': 'ir.actions.act_window_close'}
        active_ids = self._context.get('active_ids', [])
        if active_ids is None:
            return act_close
        invoices = self.env['account.invoice'].browse(active_ids).filtered(
            lambda r: (
                not r.sent and
                r.state not in ('draft', 'proforma', 'proforma2')))
        invoices.write({'sent': True})
        for invoice in invoices:
            invoice.message_post(body=_("Invoice sent"))
        return act_close
