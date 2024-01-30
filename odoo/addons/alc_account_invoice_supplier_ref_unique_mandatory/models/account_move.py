# Copyright 2023 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.account_invoice_supplier_ref_unique.models.account_move import (
    AccountMove as AccountMoveBase,
)


class AccountMove(AccountMoveBase):
    supplier_invoice_number_required = fields.Boolean(
        compute="_compute_supplier_invoice_number_required"
    )

    @api.depends("company_id", "move_type", "state")
    def _compute_supplier_invoice_number_required(self):
        for rec in self:
            rec.supplier_invoice_number_required = (
                rec.company_id.check_invoice_supplier_number_mandatory
                and rec.is_purchase_document(include_receipts=True)
                and rec.state == "posted"
            )

    @api.constrains("supplier_invoice_number", "company_id", "move_type", "state")
    def _check_mandatory_supplier_invoice_number(self):
        """Check that the supplier_invoice_number is given on invoice/refund."""
        for rec in self:
            if rec.supplier_invoice_number_required and not rec.supplier_invoice_number:
                raise ValidationError(_("The supplier invoice number is mandatory."))
