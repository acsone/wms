# Copyright 2015-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _

from odoo.addons.account.models.account_move import AccountMove as AccountMoveBase


class AccountMove(AccountMoveBase):
    def _filter_send_invoice(self, transmit_method=None):
        def f_state(r):
            return not r.is_move_sent and r.state not in (
                "draft",
                "proforma",
                "proforma2",
            )

        def f_transmit_method(r):
            return r.transmit_method_id.code == transmit_method

        def f_email(r):
            return bool(r.partner_id.email)

        filters = [f_state]
        if transmit_method:
            filters.append(f_transmit_method)
        if transmit_method == "email":
            filters.append(f_email)

        return self.filtered(lambda r: all(f(r) for f in filters))

    def _generate_send_invoice(self, transmit_method):
        """Generate jobs to send invoices."""
        invoices = self.exists()
        invoices = invoices._filter_send_invoice(transmit_method)
        method_name = f"_send_invoice_{transmit_method}"
        for invoice in invoices:
            getattr(invoice.with_delay(priority=50), method_name)()

    def _send_invoice_mail(self):
        """Generate and send an invoice by email."""
        # we need to apply the filter because the state may have
        # changed since when we delayed the job
        invoices = self.exists()._filter_send_invoice(transmit_method="mail")
        if not invoices:
            return
        invoices.write({"is_move_sent": True})
        template_invoice = self.env.ref("account.email_template_edi_invoice")
        template_refund = self.env.ref("account.email_template_edi_credit_note")
        for move_type, invoices_per_type in invoices.partition(
            lambda move: move.move_type
        ).items():
            if move_type == "out_invoice":
                template = template_invoice
            elif move_type == "out_refund":
                template = template_refund
            for invoice in invoices_per_type:
                invoice.message_post(body=_("Invoice sent"))
                template.send_mail(invoice.id)
