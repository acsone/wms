# Copyright 2023 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api
from odoo.exceptions import ValidationError

from odoo.addons.account_invoice_supplier_ref_unique.models.account_move import (
    AccountMove as AccountMoveBase,
)


class AccountMove(AccountMoveBase):
    @api.constrains("supplier_invoice_number")
    def _check_mandatory_supplier_invoice_number(self):
        """Check that the supplier_invoice_number is given on invoice/refund."""
        if any(
            rec.company_id.check_invoice_supplier_number_mandatory
            and rec.is_purchase_document(include_receipts=True)
            and not rec.supplier_invoice_number
            for rec in self
        ):
            raise ValidationError(_("The supplier invoice number is mandatory."))

    @api.model_create_multi
    def create(self, vals_list):
        purchase_types = self.get_purchase_types(include_receipts=True)
        if any(
            self.env.company.check_invoice_supplier_number_mandatory
            and "move_type" in vals
            and vals["move_type"] in purchase_types
            and "supplier_invoice_number" not in vals
            for vals in vals_list
        ):
            raise ValidationError(_("The supplier invoice number is mandatory."))
        return super().create(vals_list)
