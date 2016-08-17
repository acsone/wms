# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from base64 import b64encode
from pkg_resources import Requirement, resource_string

import anthem


@anthem.log
def setup_company(ctx, req):
    """ Configuring company data """
    company = ctx.env.ref('base.main_company')
    company.write({
        'name': 'Alcyon Belux SA',
        'street': 'Rue le Marais 17',
        'street2': '',
        'zip': '4530',
        'city': 'Villers-le-Bouillet',
        'country_id': ctx.env.ref('base.ch').id,
        'phone': '04/3383490',
        'fax': '04/3382783',
        'email': 'secretariat@alcyonbelux.be',
        'website': 'www.alcyonbelux.be',
        'vat': 'BE 0421.801.233',
        'company_registry': '',
        'rml_header1': '',
    })

    # load logo on company
    logo_content = resource_string(req, 'data/images/logo-alcyon.png')
    company.logo = b64encode(logo_content)


@anthem.log
def setup_language(ctx):
    """ Installing language and configuring locale formatting """
    for code in ('fr_BE', 'nl_BE'):
        ctx.env['base.language.install'].create({'lang': code}).lang_install()

    ctx.env['res.lang'].search([]).write({
        'grouping': '[3, 0]',
        'date_format': '%d/%m/%Y',
    })


@anthem.log
def main(ctx):
    """ Executing main entry point called before upgrade of addons """
    req = Requirement.parse('alcyon-odoo')
    setup_language(ctx)
    setup_company(ctx, req)
