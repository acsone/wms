# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_pickingtype_humain(ctx):
    picking_type = ctx.env.ref(
        '__setup__.stock_picking_type_humain',
        raise_if_not_found=False
    )
    if picking_type:
        picking_type.unlink()
    location = ctx.env.ref(
        '__setup__.stock_location_pharma',
        raise_if_not_found=False
    )
    if location:
        location.unlink()


@anthem.log
def add_missing_antibiotic_taxes(ctx):
    """ Add missing antibiotic taxes from account tax template """
    company = ctx.env.ref('base.main_company')

    missing_taxes_xmlid = (
        'l10n_be_antibiotic_tax.antibiotic_012_out',
        'l10n_be_antibiotic_tax.antibiotic_024_out',
        'l10n_be_antibiotic_tax.antibiotic_033_out',
        'l10n_be_antibiotic_tax.antibiotic_065_out',
        'l10n_be_antibiotic_tax.antibiotic_214_out',
        'l10n_be_antibiotic_tax.antibiotic_012_in',
        'l10n_be_antibiotic_tax.antibiotic_024_in',
        'l10n_be_antibiotic_tax.antibiotic_033_in',
        'l10n_be_antibiotic_tax.antibiotic_066_in',
        'l10n_be_antibiotic_tax.antibiotic_244_in'
    )
    for missing_tax_xmlid in missing_taxes_xmlid:
        template = ctx.env.ref(missing_tax_xmlid)
        # The method generate_tax will create the tax
        # OR update if the tax already existing
        template._generate_tax(company)


@anthem.log
def post(ctx):
    """ POST 10.23.3 """
    remove_pickingtype_humain(ctx)
    add_missing_antibiotic_taxes(ctx)
