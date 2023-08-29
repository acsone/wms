# Copyright 2015-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountInvoiceSent(models.TransientModel):
    """This wizard will mark as sent the all the selected validated invoices."""

    _name = "account.invoice.sent"
    _description = "Wizard to send invoices"

    _act_close = {"type": "ir.actions.act_window_close"}

    count_print = fields.Integer("To print", readonly=True)
    count_email = fields.Integer("By email", readonly=True)
    count_email_missing = fields.Integer("Email address missing", readonly=True)

    @api.model
    def _get_ids(self):
        active_ids = self._context.get("active_ids", [])
        if not active_ids or self.env.context.get("active_model", "") != "account.move":
            return False
        return active_ids

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        invoice_ids = self._get_ids()
        if not invoice_ids:
            return self._act_close
        invoices = self.env["account.move"].browse(invoice_ids)
        invoices = invoices._filter_send_invoice()
        defaults["count_print"] = len(invoices._filter_send_invoice("post"))
        invoices_email = invoices.filtered(lambda r: r.transmit_method_code == "mail")
        defaults["count_email"] = len(invoices_email)
        defaults["count_email_missing"] = len(invoices_email) - len(
            invoices_email.filtered("partner_id.commercial_partner_id.email")
        )
        return defaults

    def button_print(self):
        # TODO create a model to show the attachments and
        # create jobs on them
        invoice_ids = self._get_ids()
        if not invoice_ids:
            return self._act_close
        invoices = self.env["account.move"].browse(invoice_ids)
        invoices = invoices._filter_send_invoice("post")
        invoice_print = self.env["account.invoice.print"].create(
            {"invoice_ids": [(6, 0, invoices.ids)]}
        )
        invoice_print.with_delay(priority=20).generate_report()
        self.env.user.notify_info(_("A report will be generated in the background."))
        return self._act_close

    def _send_action(self, transmit_method):
        invoice_ids = self._get_ids()
        if not invoice_ids:
            return self._act_close
        invoices = self.env["account.move"].browse(invoice_ids)
        invoices = invoices._filter_send_invoice(transmit_method)
        invoices.with_delay(priority=50)._generate_send_invoice(transmit_method)
        return self._act_close

    def button_email(self):
        self._send_action("mail")
        self.env.user.notify_info(
            _("Invoices will be sent by email in the background.")
        )
        return self._act_close

    def button_mark_only(self):
        invoice_ids = self._get_ids()
        if not invoice_ids:
            return self._act_close
        invoices = self.env["account.move"].browse(invoice_ids)
        invoices = invoices._filter_send_invoice()
        invoices.write({"is_move_sent": True})
        for invoice in invoices:
            invoice.message_post(body=_("Invoice sent"))
        return self._act_close
