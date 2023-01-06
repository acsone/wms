# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields

from odoo.addons.account.models import account_payment_term


class AccountPaymentTerm(account_payment_term.AccountPaymentTerm):

    cash_on_delivery = fields.Boolean("Cash On Delivery")
