# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, tools

from odoo.addons.account.models.account_account import AccountAccount
from odoo.addons.account.models.account_analytic_account import AccountAnalyticAccount
from odoo.addons.account.models.account_journal import AccountJournal
from odoo.addons.account.models.account_move import AccountMove
from odoo.addons.account_analytic_tag.models.account_analytic_tag import (
    AccountAnalyticTag,
)
from odoo.addons.base.models.res_company import Company
from odoo.addons.base.models.res_currency import Currency
from odoo.addons.base.models.res_partner import Partner
from odoo.addons.product.models.product_product import ProductProduct


class AccountMoveLineWithAnalyticCategory(models.Model):
    _name = "account.move.line.with.analytic.category"
    _description = "Account move line for analytic analysis"
    _auto = False

    company_id = fields.Many2one[Company](string="Company")
    date = fields.Date(string="Date")
    account_id = fields.Many2one[AccountAccount](string="Account")
    # user_type_id replaced by account_id.account_type
    account_type = fields.Selection(
        related="account_id.account_type", string="Account Type", readonly=True
    )
    analytic_account_id = fields.Many2one[AccountAnalyticAccount](
        string="Analytic Account"
    )
    tag_1_id = fields.Many2one[AccountAnalyticTag](string="Tag 1")
    tag_2_id = fields.Many2one[AccountAnalyticTag](string="Tag 2")
    tag_3_id = fields.Many2one[AccountAnalyticTag](string="Tag 3")
    product_id = fields.Many2one[ProductProduct](string="Product")
    journal_id = fields.Many2one[AccountJournal](string="Journal")
    partner_id = fields.Many2one[Partner](string="Partner")
    company_currency_id = fields.Many2one[Currency](
        related="company_id.currency_id", readonly=True
    )
    debit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    credit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    balance = fields.Monetary(currency_field="company_currency_id")
    ref = fields.Char(related="move_id.ref", string="Reference", readonly=True)
    quantity = fields.Float(digits="Product Unit of Measure")
    move_id = fields.Many2one[AccountMove](string="Journal Entry")
    amount = fields.Monetary(
        "Amount", default=0.0, currency_field="company_currency_id"
    )
    name = fields.Char()

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            f"""CREATE OR REPLACE VIEW {self._table} AS
              ( SELECT
              aml.id,
              aml.company_id,
              aml.date,
              aml.account_id,
              aa.account_type,
              aml.analytic_account_id,
              aaa.tag_1_id,
              aaa.tag_2_id,
              aaa.tag_3_id,
              aml.product_id,
              aml.journal_id,
              aml.partner_id,
              aml.debit,
              aml.credit,
              aml.balance,
              -aml.balance as amount,
              aml.ref,
              aml.name,
              aml.quantity,
              aml.move_id
            FROM account_move_line as aml
            JOIN account_account as aa ON (aml.account_id = aa.id)
            LEFT JOIN account_analytic_account aaa ON (aaa.id = aml.analytic_account_id)
            )"""
        )
