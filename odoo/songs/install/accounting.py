# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update, add_xmlid
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def import_banks(ctx):
    """ Importing banks """
    content = resource_stream(req, 'data/demo/res.bank.csv')
    load_csv_stream(ctx, 'res.bank', content, delimiter=',')


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
def create_bank_accounts(ctx):
    """ Creating bank accounts """
    expense_type = ctx.env.ref('account.data_account_type_expenses')
    records = [
        {'xmlid': 'scenario.account_1010',
         'name': 'XXX 00-001285-1',
         'code': '991010',
         'user_type_id': expense_type.id,
         },
        {'xmlid': 'scenario.account_1020',
         'name': 'ZZZ BE7400700115500080000',
         'code': '991020',
         'user_type_id': expense_type.id,
         },
        {'xmlid': 'scenario.account_1021',
         'name': 'ZZZ BE2300700115500172222',
         'code': '991021',
         'user_type_id': expense_type.id,
         },
    ]
    for record in records:
        xmlid = record.pop('xmlid')
        create_or_update(ctx, 'account.account', xmlid, record)


@anthem.log
def create_banks(ctx):
    """ Creating banks """
    records = [
        {'xmlid': 'scenario.journal_XXXX',
         'code': 'XXXX',
         'name': 'Poste XXX',
         'account_code': '1010',
         },
        {'xmlid': 'scenario.journal_ZZZ1',
         'code': 'ZZZ1',
         'name': 'ZZZ 1',
         'account_code': '1020',
         },
        {'xmlid': 'scenario.journal_ZZZ2',
         'code': 'ZZZ2',
         'name': 'ZZZ 2',
         'account_code': '1021',
         },
    ]
    for record in records:
        xmlid = record.pop('xmlid')
        account_code = record.pop('account_code')
        account = ctx.env['account.account'].search(
            [('code', '=', account_code)],
            limit=1,
        )
        record.update({
            'type': 'bank',
            'company_id': ctx.env.ref('base.main_company').id,
            'default_debit_account_id': account.id,
            'default_credit_account_id': account.id,
            'update_posted': True,
        })
        create_or_update(ctx, 'account.journal', xmlid, record)

    records = [
        {'xmlid': 'scenario.bank_1',
         'bank_xmlid': 'scenario.bank1',
         'journal_xmlid': 'scenario.journal_XXXX',
         'acc_number': 'BE2198765430',
         },
        {'xmlid': 'scenario.bank_2',
         'bank_xmlid': 'scenario.bank2',
         'journal_xmlid': 'scenario.journal_ZZZ1',
         'acc_number': 'BE68539007547034',
         },
        {'xmlid': 'scenario.bank_3',
         'bank_xmlid': 'scenario.bank3',
         'journal_xmlid': 'scenario.journal_ZZZ2',
         'acc_number': 'BE11123456748',
         },
    ]
    for record in records:
        xmlid = record.pop('xmlid')
        bank_xmlid = record.pop('bank_xmlid')
        journal_xmlid = record.pop('journal_xmlid')
        record.update({
            'company_id': ctx.env.ref('base.main_company').id,
            'partner_id': ctx.env.ref('base.main_partner').id,
            'bank_id': ctx.env.ref(bank_xmlid).id,
            'journal_id': [(6, 0, ctx.env.ref(journal_xmlid).ids)],
        })
        create_or_update(ctx, 'res.partner.bank', xmlid, record)


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
    company_currency(ctx)
    activate_multicurrency(ctx)
    create_bank_accounts(ctx)
    create_banks(ctx)
    create_financial_journals(ctx)
    add_xmlid_account(ctx)
    adapt_chart_of_account(ctx)
