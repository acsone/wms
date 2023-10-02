# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.partner_invoicing_mode.models.account_invoice import (
    AccountMove as Move,
)


class AccountMove(Move):
    customer_call_name = fields.Char(related="partner_id.call_name", readonly=True)
    customer_invoicing_mode = fields.Selection(
        related="partner_id.invoicing_mode", readonly=True
    )
