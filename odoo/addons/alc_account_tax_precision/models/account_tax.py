# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.account.models.account_tax import AccountTax as TaxBase


class AccountTax(TaxBase):

    amount = fields.Float(required=True, digits="Taxes")
