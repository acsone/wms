# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.account_payment_mode.models.account_payment_mode import (
    AccountPaymentMode as PaymentMode,
)


class AccountPaymentMode(PaymentMode):

    invoice_description = fields.Text(
        translate=True, help="Invoicing method description"
    )
