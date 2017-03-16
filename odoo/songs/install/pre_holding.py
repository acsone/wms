# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from anthem.lyrics.records import create_or_update
import anthem


@anthem.log
def no_accounting(ctx):
    """Prepare no accounting in holding"""
    values = {
        'name': "Dummy account to delete",
        'code': "DUMMY",
        'user_type_id': ctx.env.ref('account.data_account_type_equity').id,
        }
    create_or_update(ctx, 'account.account',
                     '__setup__.dummy_holding_account', values)
    company = ctx.env.ref('base.main_company')
    company.expects_chart_of_accounts = False
