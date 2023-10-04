# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.account.models.account_move import AccountMove as AccountMoveBase


class AccountMove(AccountMoveBase):
    def _filter_payments_widget_to_reconcile_info_by_payment_mode(self):
        """Only return invoices/refunds and move lines with the same payment mode."""
        self.ensure_one()
        move_line_model = self.env["account.move.line"]
        info = self.invoice_outstanding_credits_debits_widget
        if info and info.get("content"):
            content = info["content"]
            content_filtered = []
            for line_info in content:
                line = move_line_model.browse(line_info.get("id"))
                if line.move_type != "entry" or (
                    line.move_type == "entry"
                    and line.payment_mode_id == self.payment_mode_id
                ):
                    content_filtered.append(line_info)
            if content_filtered:
                info["content"] = content_filtered
                self.invoice_outstanding_credits_debits_widget = info
                self.invoice_has_outstanding = True
            else:
                self.invoice_outstanding_credits_debits_widget = False
                self.invoice_has_outstanding = False

    def _compute_payments_widget_to_reconcile_info(self):
        res = super()._compute_payments_widget_to_reconcile_info()
        for rec in self:
            rec._filter_payments_widget_to_reconcile_info_by_payment_mode()
        return res
