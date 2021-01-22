# -*- coding: utf-8 -*-
# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools

import odoo.addons.decimal_precision as dp


class AccountMoveLineWithAnalyticCategory(models.Model):
    _name = "account.move.line.with.analytic.category"
    _auto = False

    company_id = fields.Many2one("res.company", string="Company")
    date = fields.Date(string="Date")  # related is required
    account_id = fields.Many2one("account.account", string="Account")
    user_type_id = fields.Many2one("account.account.type")
    analytic_account_id = fields.Many2one(
        "account.analytic.account", string="Analytic Account"
    )
    tag_1_id = fields.Many2one("account.analytic.tag", string="Tag 1")
    tag_2_id = fields.Many2one("account.analytic.tag", string="Tag 2")
    tag_3_id = fields.Many2one("account.analytic.tag", string="Tag 3")
    product_id = fields.Many2one("product.product", string="Product")
    journal_id = fields.Many2one("account.journal", string="Journal")
    partner_id = fields.Many2one("res.partner", string="Partner")
    company_currency_id = fields.Many2one(
        "res.currency", related="company_id.currency_id", readonly=True
    )
    debit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    credit = fields.Monetary(default=0.0, currency_field="company_currency_id")
    balance = fields.Monetary(currency_field="company_currency_id")
    ref = fields.Char(related="move_id.ref", string="Reference", readonly=True)
    quantity = fields.Float(digits=dp.get_precision("Product Unit of Measure"))
    move_id = fields.Many2one("account.move", string="Journal Entry")
    amount = fields.Monetary(
        "Amount", default=0.0, currency_field="company_currency_id"
    )
    name = fields.Char()

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(
            """CREATE OR REPLACE VIEW %s AS
              ( SELECT
              aml.id,
              aml.company_id,
              aml.date,
              aml.account_id,
              aml.user_type_id,
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
            LEFT JOIN account_analytic_account aaa ON (aaa.id = aml.analytic_account_id)
            )"""
            % self._table
        )
