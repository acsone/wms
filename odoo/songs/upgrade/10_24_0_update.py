# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import update_translations
from anthem.lyrics.records import add_xmlid


@anthem.log
def update_module_translations(ctx):
    """ Update translations for : specific_sale """
    update_translations(ctx, ['specific_sale'])


@anthem.log
def add_apb_tax_2018(ctx):
    ref = ctx.env.ref
    xmlid_old = 'l10n_be_apb_tax.1_apb_01_out'
    xmlid_2018 = 'l10n_be_apb_tax.1_apb_02_out'
    apb_tax_2018 = ref(xmlid_2018, raise_if_not_found=False)
    if not apb_tax_2018:
        apb_tax_old = ref(xmlid_old)
        apb_tax_2018 = apb_tax_old.copy()

        # rename old tax
        apb_tax_old.write({
            'name': 'APB Out (old)',
            'description': 'APB-OUT used before 2018-04-23',
        })

        # setup new tax value
        apb_tax_2018.amount = 0.02292

        # tax created by template needs to be noupdate
        add_xmlid(ctx, apb_tax_2018, xmlid_2018, noupdate=True)


@anthem.log
def pre(ctx):
    """ PRE 10.24.0 """
    update_module_translations(ctx)


@anthem.log
def post(ctx):
    """ POST 10.24.0 """
    add_apb_tax_2018(ctx)
