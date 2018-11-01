# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import os
from base64 import b64encode
from pkg_resources import resource_string

import anthem
from ..common import req


@anthem.log
def setup_company_minimal(ctx):
    """ Configuring company data """
    company = ctx.env.ref('base.main_company')
    company.write({
        'name': 'Alcyon Belux SA',
    })


@anthem.log
def setup_company(ctx):
    """ Configuring company data """
    company = ctx.env.ref('base.main_company')
    company.write({
        'name': 'Alcyon Belux SA',
        'street': 'Rue le Marais, 17',
        'street2': '',
        'zip': '4530',
        'city': 'Villers-le-Bouillet',
        'country_id': ctx.env.ref('base.be').id,
        'phone': '+32 (0)4 338 34 90',
        'fax': '+32 (0)4 338 27 83',
        'email': 'secretariat@alcyonbelux.be',
        'website': 'www.alcyonbelux.be',
        'vat': 'BE 0421.801.233',
        'company_registry': 'RC LIEGE : 138.989',
        'rml_header1': 'Une société de Vétérinaires\
         au service des Vétérinaires',
        'rml_footer': 'Phone: +32 (0)4 338 34 90 | Fax: +32 (0)4 338 27 83 | '
                      'Email: secretariat@alcyonbelux.be | '
                      'Website: http://www.alcyonbelux.be | '
                      'TIN: BE0421801233 | Reg: RC LIEGE : 138.989',
        'sepa_creditor_identifier': 'BE90ZZZ0421801233',
    })

    # load logo on company
    logo_content = resource_string(req, 'data/images/logo-alcyon.jpg')
    company.logo = b64encode(logo_content)


@anthem.log
def setup_language(ctx):
    """ Installing language and configuring locale formatting """
    # Skiping time-consuming installation language on CI
    if os.environ.get('CI'):
        ctx.log_line('CI=True => skip lang_install.')
    else:
        for code in ('fr_BE', 'nl_BE', 'de_DE'):
            ctx.env['base.language.install'].create(
                {'lang': code}).lang_install()

    ctx.env['res.lang'].search([]).write({
        'grouping': '[3, 0]',
        'date_format': '%d/%m/%Y',
    })


@anthem.log
def change_config_parameters(ctx):
    """ fix config parameters  """
    url = "http://localhost:8069"
    ctx.env['ir.config_parameter'].set_param('web.base.url', url)
    ctx.env['ir.config_parameter'].set_param('web.base.url.freeze', 'True')
    ctx.env['ir.config_parameter'].set_param(
        'database.secret', '1ad1b60d-4379-4a5f-9b0e-a20a68bf37a7')
    ctx.env['ir.config_parameter'].set_param(
        'database.expiration_date', '2017-12-31')


@anthem.log
def disable_module_account_sepa(ctx):
    """ Disable the module account_sepa """

    # The module account will automatically install l10n modules
    # however we don't want to install the module account_sepa (this module
    # is in conflict with the module account_banking_sepa_direct_debit)
    ctx.env.ref('base.module_account_sepa').write({
        'state': 'uninstallable'
    })


@anthem.log
def main(ctx):
    """ Executing main entry point called before upgrade of addons """
    setup_language(ctx)
    setup_company_minimal(ctx)
    change_config_parameters(ctx)
    disable_module_account_sepa(ctx)
