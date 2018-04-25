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

    # Define the default chunk size
    ctx.env['ir.config_parameter'].set_param('account.chunk_size', 10)
    # Default purchase tax
    purchase_tax_21 = ctx.env.ref('l10n_be.1_attn_VAT-IN-V81-21')

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
        'default_purchase_tax_id': purchase_tax_21.id,
        'module_payment_transfer': False,
        'group_analytic_account_for_sales': True,
        'group_analytic_account_for_purchases': True,
        'group_supplier_inv_check_total': True,
    }).execute()


@anthem.log
def default_values(ctx):
    """ Set some default values.
    """
    expense_account = ctx.env.ref('l10n_be.1_a604')
    ctx.env['ir.values'].search([
        ('name', '=', 'property_account_expense_categ_id')]).write({
            'value_reference': 'account.account,%d' % expense_account.id})

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
        'value_unpickle': 'partner_ref',
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

    # The journal "Miscellaneous Operations" doesn't have a XML ID
    # and therefore cannot be exported in a PO file.
    # We will write the journal with the language FR to translate it.
    # Note: The write with an another language WILL NOT change
    # the original journal name but only translate the name in French.
    miscellaneous_operations = ctx.env['account.journal'].search(
        [('name', '=', 'Miscellaneous Operations')])
    miscellaneous_operations.with_context(lang='fr_BE').write({
        'name': 'Opérations Diverses'
    })

    # Cash journal must be of type Miscellaneous as entries are encoded
    # manually
    cash = ctx.env['account.journal'].search(
        [('name', '=', 'Cash')])
    cash.write({'type': 'general'})

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
def set_fiscal_position_country(ctx):
    ctx.env.ref('__setup__.fiscal_position_nat').write({
        'auto_apply': 1,
        'country_id': ctx.env.ref('base.be').id,
    })
    ctx.env.ref('__setup__.fiscal_position_intra').write({
        'auto_apply': 1,
        'country_group_id': ctx.env.ref('base.europe').id,
    })
    ctx.env.ref('__setup__.fiscal_position_extra').write({
        'auto_apply': 1,
    })


@anthem.log
def set_fiscal_position_mention(ctx):
    """ Set legal mention on fiscal position """
    ctx.env.ref('__setup__.fiscal_position_extra').write({
        'note': 'Article 39 – exportation de biens'
    })
    ctx.env.ref('__setup__.fiscal_position_intra').write({
        'note': 'Autoliquidation Art 39 bis – livraison intracommunautaire'
    })


@anthem.log
def adapt_chart_of_account(ctx):
    """ Adapt chart of account """
    content = resource_stream(req, 'data/install/account.account.csv')
    load_csv_stream(ctx, 'account.account', content, delimiter=',')
    model = 'account.fiscal.position.account'
    content = resource_stream(req, 'data/install/%s.csv' % model)
    load_csv_stream(ctx, model, content, delimiter=',')


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
    add_xmlid(
        ctx, customer_journal,
        '__setup__.account_journal_customer_invoices',
        noupdate=True
    )
    customer_journal.sequence_id.write({
        'prefix': 'FV/%(range_year)s/',
        'padding': 5,
        'use_date_range': True,
    })
    refund_seq = create_or_update(
        ctx, 'ir.sequence', '__setup__.customer_invoice_refund_seq', {
            'name': 'Customer Invoices Refund',
            'prefix': 'NCV/%(range_year)s/',
            'padding': 5,
            'use_date_range': True,
            'implementation': 'no_gap',
        }
    )
    customer_journal.write({
        'refund_sequence': True,
        'refund_sequence_id': refund_seq.id,
    })

    ctx.env['ir.sequence'].search([
        ('prefix', 'ilike', 'MISC'),
        ]).write({'prefix': 'OD/%(range_year)s/%(range_month)s/'})

    purchase_journals = journals.filtered(lambda r: r.type == 'purchase')
    for seq in (purchase_journals.mapped('sequence_id') |
                purchase_journals.mapped('refund_sequence_id')):
        if 'range_month' not in seq.prefix:
            seq.prefix = seq.prefix + '%(range_month)s/'

    ctx.env['ir.sequence'].search([
        ('prefix', 'ilike', 'range_year'),
        ('prefix', 'not ilike', 'range_month'),
        ]).write({'use_end_date': True})


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
    """ Importing account payment term. Do not load translations, the note is
    not displayed on the invoice, only the due date """
    content = resource_stream(req, 'data/install/account.payment.term.csv')
    load_csv_stream(ctx, 'account.payment.term', content, delimiter=',')
    lines = resource_stream(req, 'data/install/account.payment.term.line.csv')
    load_csv_stream(ctx, 'account.payment.term.line', lines, delimiter=',')


@anthem.log
def activate_check_on_vat(ctx):
    """ Activate check on vat """

    # We want to activate this check after having import data
    # to avoid to have an error on vat which became invalid on db2 database
    ctx.env.ref('base.main_company').write({
        'vat_check_vies': True,
    })


@anthem.log
def setup_cutoff(ctx):
    ref = ctx.env.ref
    company = ctx.env.ref('base.main_company')
    journal = ctx.env.ref('__setup__.accrual_journal')
    company.write({
        'default_cutoff_journal_id': journal.id,
        'default_accrued_revenue_account_id': ref('l10n_be.1_a404').id,
        'default_accrued_expense_account_id': ref('l10n_be.1_a444').id,
        'default_accrued_revenue_return_account_id':
            ref('__setup__.account_404100').id,
        'default_accrued_expense_return_account_id':
            ref('__setup__.account_444100').id,
        })
    taxes = ctx.env['account.tax'].search([])
    taxes.write({
        'account_accrued_revenue_id': ref('l10n_be.1_a404').id,
        'account_accrued_expense_id': ref('l10n_be.1_a444').id,
        })


@anthem.log
def setup_intrastat(ctx):
    # Do not declare goods inside country
    ctx.env.ref('base.be').intrastat = False


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
    default_values(ctx)
    company_settings(ctx)
    company_currency(ctx)
    activate_multicurrency(ctx)
    add_xmlid_fiscal_position(ctx)
    set_fiscal_position_country(ctx)
    set_fiscal_position_mention(ctx)
    settings(ctx)
    setup_sequences(ctx)
    set_esb_references(ctx)
    import_account_payment_term(ctx)
    setup_cutoff(ctx)
    setup_intrastat(ctx)
