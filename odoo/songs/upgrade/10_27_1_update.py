# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import update_translations


@anthem.log
def update_translation_for_specific_followup(ctx):
    """ Update translations for specific_followup """

    # Translations for noupdate fields cannot be updated by an update
    # of translation (even with --18n-overwrite).
    # We need to remove these translations first
    ctx.env['ir.translation'].search([
        ('module', '=', 'specific_followup')
    ]).unlink()

    # Odoo save existing followup letters in a temporary table (TransientModel)
    # We need to delete all existing letters to use new translations
    ctx.env['account.report.context.followup.all'].search([]).unlink()
    ctx.env['account.report.context.followup'].search([]).unlink()

    update_translations(ctx, ['specific_followup'])


@anthem.log
def remove_customer_supplier_balance(ctx):
    """ Remove customer and supplier balance """
    balance_customer = ctx.env.ref(
        '__setup__.account_move_balance_customer', raise_if_not_found=False)
    if balance_customer:
        balance_customer.unlink()

    balance_supplier = ctx.env.ref(
        '__setup__.account_move_balance_supplier', raise_if_not_found=False)
    if balance_supplier:
        balance_supplier.unlink()


@anthem.log
def post(ctx):
    """ POST 10.27.1 """
    update_translation_for_specific_followup(ctx)
    remove_customer_supplier_balance(ctx)
