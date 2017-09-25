# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream

import anthem
from anthem.lyrics.records import create_or_update, add_xmlid
from anthem.lyrics.loaders import load_csv_stream

from ..common import req


@anthem.log
def no_coa_instance_lock(ctx):
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


@anthem.log
def no_coa_instance_unlock(ctx):
    """ Remove dummy account on main company """
    ctx.env.ref('__setup__.dummy_holding_account').unlink()


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
        'group_supplier_inv_check_total': True,
    }).execute()

    ctx.env.ref('base.main_company').write({
        'vat_check_vies': True,
    })


@anthem.log
def default_values(ctx):
    """ Set some default values.
    """
    create_or_update(ctx, 'ir.values', '__setup__.res_partner_default_bba', {
        'key': 'default',
        'name': 'out_inv_comm_type',
        'model': 'res.partner',
        'value_unpickle': 'bba',
        'key2': None,
    })
    create_or_update(ctx, 'ir.values', '__setup__.res_partner_bba_random', {
        'key': 'default',
        'name': 'out_inv_comm_algorithm',
        'model': 'res.partner',
        'value_unpickle': 'random',
        'key2': None,
    })

    account_612031 = ctx.env.ref('__setup__.account_612031')
    tax_xml_id = 'l10n_be.1_attn_VAT-IN-V82-CAR-EXC-C1'
    create_or_update(ctx, 'account.tax', tax_xml_id, {
        'account_id': account_612031.id,
        'refund_account_id': account_612031.id
    })


@anthem.log
def company_settings(ctx):
    company = ctx.env.ref('base.main_company')
    company.write({
        'order_phone': '+32 (0)4 338 84 39',
        'order_fax': '+32 (0)4 338 34 79',
        'invoice_terms_conditions':
            "Sauf stipulation écrite contraire, nos factures sont payables "
            "au comptant.  Toute somme demeurée impayée à son échéance donne "
            "de plein droit lieu à des intérêts de retard calculés "
            "conformément au taux d’intérêt en vigueur de la Banque Nationale,"
            " augmenté de 1%, sans qu’une mise en demeure préalable "
            "ne soit nécessaire.  "
            "Le montant dû sera en outre majoré d’une indemnité forfaitaire "
            "de 10% avec un minimum de 40 € par facture.  "
            "Les litiges éventuels relèvent exclusivement de la justice "
            "de paix du canton ou des tribunaux de l’arrondissement "
            "où est établi notre siège social.\n"
            "Dans l'hypothèse où le client devrait être considéré comme un "
            "consommateur au sens de la loi du 6 avril 2010 relative aux "
            "pratiques du marché et à la protection du consommateur, "
            "la clause pénale précitée serait également applicable à la "
            "S.A. Alcyon dans le cas où elle n'exécuterait pas ses propres "
            "obligations contractuelles (clause de réciprocité).\n"
            "Nos conditions générales de vente complètes peuvent vous être "
            "envoyées sur demande et sont consultables sur le site internet "
            "http://www.alcyonbelux.be",
    })

    company.with_context(lang='nl_BE').write({'invoice_terms_conditions': (
        "Behalve indien uitdrukkelijk, zijn onze facturen contant betaalbaar. "
        "Elke bedrag die op de vervaldag niet betaald zijn, zullen van "
        "rechtswege en zonder voorafgaande ingebrekestelling een interest "
        "opbrengen gelijk aan de rentevoet vande Nationale Bank, "
        "verhoogd met 1%.. Ze worden bovendien van rechtswege en zonder "
        "voorafgaande ingebrekestelling vermeerderd met een schadevergoeding "
        "gelijk aan 10% van het bedrag dat op de vervaldag niet betaald is, "
        "met een minimum van € 40,00.per faktuur.  In geval van geschil, zijn "
        "de rechtbanken van Luik alleen bevoegd\n"
        "Als de klant als een consument moet worden beschouwd in de  zin van "
        "de wet van 6 april 2010 betreffende marktpraktijken en "
        "consumentenbescherming,  is de voornoemde strafclausule tevens van "
        "toepassing op de N.V. Alcyon wanneer die haar contractuele "
        "verplichtingen niet nakomt (wederkerigheidsclausule).\n"
        "Zie algemene verkoops op http://www.alcyonbelux.be.  "
        "Een papieren exemplaar wordt op annvraag kosteloos aan u verstrekt."
    )})


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

    # Set the flag "update_posted" on following journals
    # These journals have no XMLid
    journals_to_flag = ctx.env['account.journal'].search([
        ('code', 'in', ['STJ', 'BILL', 'EXP', 'INV', 'MISC'])
    ])
    journals_to_flag.write({
        'update_posted': True
    })


@anthem.log
def import_account_analytic_tag(ctx):
    """ Importing account analytic tags """
    content = resource_stream(req, 'data/install/account.analytic.tag.csv')
    load_csv_stream(ctx, 'account.analytic.tag', content, delimiter=',')


@anthem.log
def import_account_analytic_account(ctx):
    """ Importing account analytic account """
    content = resource_stream(req, 'data/install/account.analytic.account.csv')
    load_csv_stream(ctx, 'account.analytic.account', content, delimiter=',')


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
        {'xmlid': '__setup__.expense_journal',
         'name': 'Expenses',
         'code': 'EXP',
         'type': 'purchase',
         },
        {'xmlid': '__setup__.wage_journal',
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
            '__setup__.account_' + account.code,
            noupdate=True
            )


@anthem.log
def add_xmlid_fiscal_position(ctx):
    fiscal_positions = ctx.env['account.fiscal.position'].search([])
    for pos in fiscal_positions:
        if 'Extra' in pos.name:
            code = 'extra'
        elif 'Intra' in pos.name:
            code = 'intra'
        elif 'National' in pos.name:
            code = 'nat'
        else:
            code = 'cocontractor'

        add_xmlid(
            ctx, pos,
            '__setup__.fiscal_position_' + code,
            noupdate=True
            )


@anthem.log
def adapt_chart_of_account(ctx):
    """ Adapt chart of account """
    content = resource_stream(req, 'data/install/account.account.csv')
    load_csv_stream(ctx, 'account.account', content, delimiter=',')


@anthem.log
def setup_sequences(ctx):
    """ Configure invoicing sequences """
    company = ctx.env.ref('base.main_company')
    journals = ctx.env['account.journal'].search(
        [('company_id', '=', company.id)]
    )

    customer_journal = journals.filtered(
        lambda a: a.name == 'Customer Invoices'
    )

    customer_journal.sequence_id.write({
        'prefix': 'FV/17/',
        'padding': 5,
        'use_date_range': False,
    })

    refund_seq = create_or_update(
        ctx, 'ir.sequence', '__setup__.customer_invoice_refund_seq', {
            'name': 'Customer Invoices Refund',
            'prefix': 'NCV/17/',
            'padding': 5,
            'use_date_range': False,
            'implementation': 'no_gap',
        }
    )
    customer_journal.write({
        'refund_sequence': True,
        'refund_sequence_id': refund_seq.id,
    })


@anthem.log
def configure_missing_chart_of_account(ctx):
    """Configure Missing COA for companies"""

    coa_dict = {
        'base.main_company': {
            'chart_template_id': 'l10n_be.l10nbe_chart_template',
            'template_transfer_account_id': 'l10n_be.trans',
            'sale_tax_id': 'l10n_be.attn_VAT-OUT-21-L',
            'purchase_tax_id': 'l10n_be.attn_VAT-IN-V81-21',
        },
    }
    for company_xml_id, values in coa_dict.iteritems():
        company = ctx.env.ref(company_xml_id)
        coa = ctx.env.ref(values['chart_template_id'])
        template_transfer_account = ctx.env.ref(
            values['template_transfer_account_id']
        )
        sale_tax = ctx.env.ref(values['sale_tax_id'])
        purchase_tax = ctx.env.ref(values['purchase_tax_id'])
        if not company.chart_template_id:
            wizard = ctx.env['wizard.multi.charts.accounts'].create({
                'company_id': company.id,
                'chart_template_id': coa.id,
                'transfer_account_id': template_transfer_account.id,
                'sale_tax_id': sale_tax.id,
                'purchase_tax_id': purchase_tax.id,
                'complete_tax_set': coa.complete_tax_set,
                'currency_id': ctx.env.ref('base.EUR').id,
                'bank_account_code_prefix': coa.bank_account_code_prefix,
                'cash_account_code_prefix': coa.cash_account_code_prefix,
            })
            wizard.execute()


@anthem.log
def create_account_types(ctx):
    """ Creating Account Types """

    account_type_xml_id = '__setup__.account_type_annexes_hors_bilan'
    create_or_update(ctx, 'account.account.type', account_type_xml_id, {
        'name': 'ANNEXES/HORS BILAN',
        'type': 'other',
        'analytic_policy': 'optional',
        'include_initial_balance': False,
    })


@anthem.log
def set_esb_references(ctx):
    """ Set ESB references """
    refs = (
        ('l10n_be.1_attn_VAT-IN-V81-00', '0'),
        ('l10n_be.1_attn_VAT-IN-V81-06', '1'),
        ('l10n_be.1_attn_VAT-IN-V81-12', '2'),
        ('l10n_be.1_attn_VAT-IN-V81-21', '3'),
    )
    for xmlid, esb_ref in refs:
        ctx.env.ref(xmlid).esb_ref = esb_ref


@anthem.log
def import_account_payment_term(ctx):
    """ Importing account payment term """
    ctx.env.ref('account.account_payment_term_immediate').unlink()
    ctx.env.ref('account.account_payment_term_15days').unlink()
    ctx.env.ref('account.account_payment_term_net').unlink()

    content = resource_stream(req, 'data/install/account.payment.term.csv')
    load_csv_stream(ctx, 'account.payment.term', content, delimiter=',')
    lines = resource_stream(req, 'data/install/account.payment.term.line.csv')
    load_csv_stream(ctx, 'account.payment.term.line', lines, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring accounting """
    configure_missing_chart_of_account(ctx)
    import_banks(ctx)
    add_xmlid_account(ctx)
    create_account_types(ctx)
    adapt_chart_of_account(ctx)
    import_account_journal(ctx)
    import_account_analytic_tag(ctx)
    import_account_analytic_account(ctx)
    company_settings(ctx)
    company_currency(ctx)
    activate_multicurrency(ctx)
    create_financial_journals(ctx)
    add_xmlid_fiscal_position(ctx)
    settings(ctx)
    setup_sequences(ctx)
    set_esb_references(ctx)
    import_account_payment_term(ctx)
