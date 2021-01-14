# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    # Split vendor invoice number and payment communication
    # Use reference for the communication as it is used in the SEPA payment and
    # reconciliation
    reference = fields.Char("Payment Communication", copy=False)
    supplier_invoice_number = fields.Char(
        "Vendor Reference",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )

    _sql_constraints = [
        (
            "unique_invoice_number_by_supplier",
            "unique (type, company_id, commercial_partner_id, "
            "supplier_invoice_number)",
            "The supplier invoice number must be unique per supplier",
        )
    ]

    @api.onchange("supplier_invoice_number", "reference_type")
    def onchange_supplier_invoice_number(self):
        """
        Set the reference with the supplier invoice number
        if the reference is empty
        and the reference type is "Free Communication"
        :return:
        """
        self.ensure_one()
        if not self.supplier_invoice_number:
            return
        if not self.reference:
            self.reference = self.supplier_invoice_number

    @api.onchange("partner_id")
    def onchange_bba_partner(self):
        reference_type = "none"
        if self.partner_id and (self.type == "out_invoice"):
            reference_type = self.partner_id.out_inv_comm_type
        self.reference_type = reference_type or "none"

    @api.onchange("reference_type")
    def onchange_bba_referencetype(self):
        reference = False
        if self.partner_id and (self.type == "out_invoice"):
            if self.reference_type:
                reference = self.generate_bbacomm(
                    self.type, self.reference_type, self.partner_id.id, ""
                )["value"]["reference"]
        self.reference = reference

    def _check_invoice_reference(self):
        # Do not check uniqueness on reference
        # We require uniqueness on supplier_invoice_number through the
        # sql_constraint
        return

    # pylint: disable=W0622
    @api.multi
    def generate_bbacomm(self, type, reference_type, partner_id, reference):
        """ Support 1-6 digit partner reference number (instead of 3-7)
        Left pad with 0 on 6 digits (instead of right pad with 0 on 7 digits).
        Extend sequence to 9999 (instead of 999)"""
        reference = reference or ""
        algorithm = False
        if partner_id:
            partner = self.env["res.partner"].browse(partner_id)
            algorithm = partner.out_inv_comm_algorithm
        algorithm = algorithm or "random"
        if (
            type != "out_invoice"
            or reference_type != "bba"
            or algorithm != "partner_ref"
            or self.check_bbacomm(reference)
        ):
            return super(AccountInvoice, self).generate_bbacomm(
                type, reference_type, partner_id, reference
            )

        partner_ref = self.env["res.partner"].browse(partner_id).ref
        partner_ref_nr = re.sub(r"\D", "", partner_ref or "")
        if len(partner_ref_nr) > 6:
            raise UserError(
                _(
                    "The partner reference cannot exceed 6 digits for the "
                    "generation of BBA Structured Communication!"
                )
            )

        partner_ref_nr = partner_ref_nr.rjust(6, "0")
        seq = "0001"
        invoice = self.search(
            [
                ("type", "=", "out_invoice"),
                ("reference_type", "=", "bba"),
                (
                    "reference",
                    "like",
                    u"+++{}/{}%".format(partner_ref_nr[:3], partner_ref_nr[3:]),
                ),
            ],
            order="reference desc",
            limit=1,
        )
        if invoice:
            prev_seq = int(invoice.reference[10:15].replace("/", ""))
            if prev_seq == 9999:
                raise UserError(
                    _(
                        "The maximum of outgoing invoices for this partner "
                        "reference has been reached"
                    )
                )

            seq = "%04d" % (prev_seq + 1)

        bbacomm = partner_ref_nr + seq
        base = int(bbacomm)
        mod = base % 97 or 97
        bbacomm += "%02d" % mod
        reference = u"+++{}/{}/{}+++".format(bbacomm[0:3], bbacomm[3:8], bbacomm[8:])
        return {"value": {"reference": reference}}
