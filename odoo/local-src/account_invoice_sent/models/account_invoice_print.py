# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import logging
import os
import tempfile
from contextlib import closing

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

    @job(default_channel='root.background.invoice_print')  # priority=40
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

        attachment = self.env['report']._check_attachment_use(
            invoices.sorted(key=lambda r: r.partner_id.ref).ids,
            self.env['report']._get_report_from_name('account.report_invoice'),
        )
        pdfdocuments = []
        for document_id, document in attachment['loaded_documents'].items():
            pdfreport_fd, pdfreport_path = tempfile.mkstemp(
                suffix='.pdf', prefix='report.tmp.'
            )
            if attachment and document:
                with closing(os.fdopen(pdfreport_fd, 'w')) as pdfreport:
                    pdfreport.write(document)
                pdfdocuments.append(pdfreport_path)

        # adding missing documents that weren't already generated
        expected_invoice_ids = set(invoices.ids)
        found_invoice_ids = set(attachment['loaded_documents'].keys())
        missing_invoice_ids = expected_invoice_ids - found_invoice_ids
        if missing_invoice_ids:
            missing_invoices = self.env['account.invoice'].browse(
                missing_invoice_ids
            )
            pdfstr = self.env['report'].get_pdf(
                missing_invoices.sorted(key=lambda r: r.partner_id.ref).ids,
                'account.report_invoice',
            )
            pdfreport_fd, pdfreport_path = tempfile.mkstemp(
                suffix='.pdf', prefix='report.tmp.'
            )
            if pdfstr:
                with closing(os.fdopen(pdfreport_fd, 'w')) as pdfreport:
                    pdfreport.write(pdfstr)
                    pdfdocuments.append(pdfreport_path)

        pdf = self.env['report']._merge_pdf(pdfdocuments)

        # Manual cleanup of the temporary files
        for document in pdfdocuments:
            try:
                os.unlink(document)
            except (OSError, IOError):
                logging.getLogger(__name__).error(
                    'Error when trying to remove file %s' % document
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
