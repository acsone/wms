# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64

from odoo import _, fields, models
from odoo.addons.queue_job.job import job


class AccountInvoicePrint(models.Model):
    _name = 'account.invoice.print'

    invoice_ids = fields.Many2many(
        comodel_name='account.invoice', readonly=True
    )
    send_email_copy = fields.Boolean(readonly=True)
    document = fields.Binary(
        comodel_name='ir.attachment', attachment=True, readonly=True
    )
    fname = fields.Char(compute='_compute_file_name')
    state = fields.Selection(
        selection=[('progress', 'In Progress'), ('done', 'Done')],
        required=True,
        readonly=True,
        default='progress',
    )

    def _compute_file_name(self):
        for record in self:
            record.fname = 'account_invoice_print_{}.pdf'.format(self.id)

    @job(default_channel='root.background.invoice_print')  # priority=20
    def generate_report(self):
        """Generate a pdf report for all invoices"""
        self.ensure_one()
        # we need to apply the filter because the state may have
        # changed since when we delayed the job
        invoices = self.invoice_ids._filter_send_invoice(
            sending_method='letter'
        )

        self.state = 'done'

        if not invoices:
            return

        template = self.env.ref('account.email_template_edi_invoice')
        for invoice in invoices:
            invoice.message_post(body=_("Invoice sent"))
            if self.send_email_copy:
                template.send_mail(invoice.id)
        pdf = self.env['report'].get_pdf(
            invoices.sorted(key=lambda r: r.partner_id.ref).ids,
            'account.report_invoice',
        )
        self.document = base64.b64encode(pdf)
        invoices.write({'sent': True})

        action_xmlid = 'account_invoice_sent.action_account_invoice_print_form'
        action = self.env.ref(action_xmlid).read()[0]
        action.update({'res_id': self.id, 'views': [(False, 'form')]})
        self.env.user.notify_info(
            _('A report for invoices is available.'),
            sticky=True,
            action=action,
        )

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('account.action_invoice_tree1').read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [
                (self.env.ref('account.invoice_form').id, 'form')
            ]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
