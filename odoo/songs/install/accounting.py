# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update, add_xmlid
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def settings(ctx):
    """ Configure the Accounting Settings.
    """
    tax_21 = ctx.env['account.tax'].search([('name', '=', '21%')])
    assert len(tax_21) == 1, "Unable to find tax"

    ctx.env['account.config.settings'].create({
        'fiscalyear_last_month': 9,
        'fiscalyear_last_day': 30,
        'module_account_reports': True,
        'group_multi_currency': False,
        'group_analytic_accounting': True,
        'module_account_budget': True,
        'module_account_bank_statement_import_ofx': False,
        'module_account_sepa': True,
        'group_proforma_invoices': True,
        'module_account_reports_followup': True,
        'default_sale_tax_id': tax_21.id,
        'module_payment_transfer': False,
        'group_analytic_account_for_sales': True,
        'group_analytic_account_for_purchases': True,
    }).execute()


@anthem.log
def import_banks(ctx):
    """ Importing banks """
    content = resource_stream(req, 'data/install/res.bank.csv')
    load_csv_stream(ctx, 'res.bank', content, delimiter=',')


@anthem.log
def import_account_journal(ctx):
    """ Import account journal
    """
    # Suppression du compte par défaut
    default_bank = ctx.env['account.journal'].search([('name', '=', 'Bank')])
    default_bank.unlink()

    content = resource_stream(req, 'data/install/account.journal.csv')
    load_csv_stream(ctx, 'account.journal', content, delimiter=',')


@anthem.log
def company_currency(ctx):
    """ Setting company's currency """
    company = ctx.env.ref('base.main_company')
    company.currency_id = ctx.env.ref('base.EUR')


@anthem.log
def activate_multicurrency(ctx):
    """ Activating multi-currency """
    employee_group = ctx.env.ref('base.group_user')
    employee_group.write({
        'implied_ids': [(4, ctx.env.ref('base.group_multi_currency').id)]
    })


@anthem.log
def create_financial_journals(ctx):
    """ Creating financial journals """
    records = [
        {'xmlid': 'scenario.expense_journal',
         'name': 'Expenses',
         'code': 'EXP',
         'type': 'purchase',
         },
        {'xmlid': 'scenario.wage_journal',
         'name': 'Wage',
         'code': 'WAG',
         'type': 'purchase',
         },
    ]
    for record in records:
        xmlid = record.pop('xmlid')
        record.update({
            'company_id': ctx.env.ref('base.main_company').id,
        })
        create_or_update(ctx, 'account.journal', xmlid, record)


@anthem.log
def add_xmlid_account(ctx):
    accounts = ctx.env['account.account'].search([])
    for account in accounts:
        add_xmlid(
            ctx, account,
            'scenario.account_' + account.code,
            noupdate=True
            )


@anthem.log
def adapt_chart_of_account(ctx):
    """ Adapt chart of account """
    content = resource_stream(req, 'data/install/account.account.csv')
    load_csv_stream(ctx, 'account.account', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring accounting """
    import_banks(ctx)
    import_account_journal(ctx)
    company_currency(ctx)
    activate_multicurrency(ctx)
    create_financial_journals(ctx)
    add_xmlid_account(ctx)
    adapt_chart_of_account(ctx)
    settings(ctx)
