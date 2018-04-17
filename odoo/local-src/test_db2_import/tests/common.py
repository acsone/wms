# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
from os import path

from odoo.tests.common import SavepointCase

SO_COLS = (
    "eccctr VARCHAR,"
    "eccsui INTEGER,"
    "eccuti INTEGER,"
    "eccrep INTEGER,"
    "eccres INTEGER,"
    "ecctyc INTEGER,"
    "eccsuc VARCHAR,"
    "eccssu VARCHAR,"
    "eccdss INTEGER,"
    "eccdaa INTEGER,"
    "eccdmm INTEGER,"
    "eccdjj INTEGER,"
    "eccrgn DOUBLE PRECISION,"
    "eccrgf DOUBLE PRECISION,"
    "eccdiv DOUBLE PRECISION,"
    "ecccli DOUBLE PRECISION,"
    "eccclf DOUBLE PRECISION,"
    "eccrin VARCHAR,"
    "eccrcl VARCHAR,"
    "ecclss INTEGER,"
    "ecclaa INTEGER,"
    "ecclmm INTEGER,"
    "eccljj INTEGER,"
    "eccmdl INTEGER,"
    "eccrem DOUBLE PRECISION,"
    "eccrms DOUBLE PRECISION,"
    "eccdev DOUBLE PRECISION,"
    "ecctau DOUBLE PRECISION,"
    "eccsec INTEGER,"
    "ecctou INTEGER,"
    "eccdel INTEGER,"
    "eccnal INTEGER,"
    "eccqua DOUBLE PRECISION,"
    "eccqte DOUBLE PRECISION,"
    "ecced1 DOUBLE PRECISION,"
    "ecced2 DOUBLE PRECISION,"
    "ecced3 DOUBLE PRECISION,"
    "ecccom DOUBLE PRECISION,"
    "eccedc DOUBLE PRECISION,"
    "eccnfa DOUBLE PRECISION,"
    "eccnne DOUBLE PRECISION,"
    "eccncd DOUBLE PRECISION,"
    "eccjes DOUBLE PRECISION,"
    "ecctes DOUBLE PRECISION,"
    "eccexo DOUBLE PRECISION,"
    "eccnof VARCHAR,"
    "eccfss INTEGER,"
    "eccfaa INTEGER,"
    "eccfmm INTEGER,"
    "eccfjj INTEGER,"
    "ecccss INTEGER,"
    "ecccaa INTEGER,"
    "ecccmm INTEGER,"
    "ecccjj INTEGER,"
    "eccmss INTEGER,"
    "eccmaa INTEGER,"
    "eccmmm INTEGER,"
    "eccmjj INTEGER,"
    "eccpss INTEGER,"
    "eccpaa INTEGER,"
    "eccpmm INTEGER,"
    "eccpjj INTEGER,"
    "eccana VARCHAR,"
    "eccdnl DOUBLE PRECISION,"
    "eccmto DOUBLE PRECISION,"
    "eccncr DOUBLE PRECISION,"
    "eccsts DOUBLE PRECISION,"
    "eccre  VARCHAR,"
    "ecccex DOUBLE PRECISION")

SOL_COLS = (
 "dccctr VARCHAR,"
 "dccsui INTEGER,"
 "dccuti INTEGER,"
 "dccnli DOUBLE PRECISION,"
 "dccsuc VARCHAR,"
 "dccssu VARCHAR,"
 "dccncl DOUBLE PRECISION,"
 "dcccli DOUBLE PRECISION,"
 "dccart VARCHAR,"
 "dcclib VARCHAR,"
 "dccquc DOUBLE PRECISION,"
 "dccqur DOUBLE PRECISION,"
 "dccqul DOUBLE PRECISION,"
 "dccexc DOUBLE PRECISION,"
 "dccaut DOUBLE PRECISION,"
 "dccbss INTEGER,"
 "dccbaa INTEGER,"
 "dccbse INTEGER,"
 "dcclss INTEGER,"
 "dcclaa INTEGER,"
 "dcclmm INTEGER,"
 "dccljj INTEGER,"
 "dccpac DOUBLE PRECISION,"
 "dccprv DOUBLE PRECISION,"
 "dccpvd DOUBLE PRECISION,"
 "dccpvn DOUBLE PRECISION,"
 "dccpve DOUBLE PRECISION,"
 "dcctva DOUBLE PRECISION,"
 "dccrem DOUBLE PRECISION,"
 "dccres DOUBLE PRECISION,"
 "dccunv DOUBLE PRECISION,"
 "dccgro DOUBLE PRECISION,"
 "dccsgr DOUBLE PRECISION,"
 "dcccvv DOUBLE PRECISION,"
 "dcccan DOUBLE PRECISION,"
 "dcccgr DOUBLE PRECISION,"
 "dccsta DOUBLE PRECISION,"
 "dccstb DOUBLE PRECISION,"
 "dccstc DOUBLE PRECISION,"
 "dccstd DOUBLE PRECISION,"
 "dccste DOUBLE PRECISION,"
 "dccstf DOUBLE PRECISION,"
 "dccpsp DOUBLE PRECISION,"
 "dccnfa VARCHAR,"
 "dccfss INTEGER,"
 "dccfaa INTEGER,"
 "dccfmm INTEGER,"
 "dccfjj INTEGER,"
 "dcccss INTEGER,"
 "dcccaa INTEGER,"
 "dcccmm INTEGER,"
 "dcccjj INTEGER,"
 "dccmss INTEGER,"
 "dccmaa INTEGER,"
 "dccmmm INTEGER,"
 "dccmjj INTEGER,"
 "dcclll INTEGER,"
 "dcclop VARCHAR,"
 "dccarc VARCHAR,"
 "dccre  VARCHAR")


SQL_PATH = path.join(path.dirname(__file__), "sql", "%s.sql")
CSV_PATH = path.join(path.dirname(__file__), "data", "%s.csv")

# Don't copy files of this project
# Quite ugly but this avoid to copy the files in the project
# we need some of those data in the tests
INSTALL_CSV_PATH = path.join("/opt/odoo/data/install", "%s.csv")


def load_csv(model, csv_file, **fmtparams):
    rows = csv.reader(csv_file, **fmtparams)
    header = next(rows)
    rows = [r for r in rows]
    result = model.load(header, rows)
    ids = result['ids']
    if not ids:
        messages = u'\n'.join(
            u'- %s' % msg for msg in result['messages']
        )
        raise Exception(u'Could not import CSV. %s' % messages)


class DB2ImportTestCase(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(DB2ImportTestCase, cls).setUpClass()
        cls.create_db2_tables()
        cls.insert_db2_records()
        cls.load_uom()
        cls.update_chart_of_account()
        cls.add_xmlid_fiscal_position()
        cls.load_accounts()
        cls.load_banks()
        cls.load_carriers()
        cls.load_account_journals()
        cls.add_xmlid_journal()
        cls.load_account_payment_modes()
        cls.load_account_payment_terms()
        cls.load_users()
        cls.load_partner_title()
        cls.load_suppliers()
        cls.create_locations()
        cls.setup_warehouse()
        cls.create_picking_types()
        cls.create_procurement_rules()
        cls.create_routes()
        cls.load_products()
        cls.load_pricelists()
        cls.load_customer_categories()
        cls.load_customers()

    @classmethod
    def add_xmlid(cls, record, xmlid):
        IMD = cls.env['ir.model.data']
        module, name = xmlid.split('.')
        IMD.create({
            'name': name,
            'module': module,
            'model': record._name,
            'res_id': record.id,
            'noupdate': True,
        })

    @classmethod
    def create_db2_tables(cls):
        """Create tables to use in tests."""

        db2_so_table = cls.env.ref('db2_import.db2_table_pentcdcl_for_sale')
        db2_sol_table = cls.env.ref('db2_import.db2_table_pdetcdcl_for_sale')

        db2_so_table._create_db2_table(SO_COLS)
        db2_sol_table._create_db2_table(SOL_COLS)

    @classmethod
    def insert_db2_records(cls):
        """Insert records to use in tests."""
        cr = cls.env.cr
        for table in ['db2_pentcdcl', 'db2_pdetcdcl']:
            with open(SQL_PATH % table) as sql_file:
                sql = sql_file.read()
                cr.execute(sql)

    @classmethod
    def get_row_from_suite(cls, suite):
        cr = cls.env.cr
        query = 'SELECT id FROM %s WHERE %s = %%s' % (
            cls._table, cls._suite_col)
        cr.execute(query, (suite, ))
        res = cr.fetchone()
        if res:
            return res[0]
        return None

    @classmethod
    def update_chart_of_account(cls):
        """ Update fiscal positions of Chart of account """
        company = cls.env.ref('base.main_company')
        coa = cls.env.ref('l10n_be.l10nbe_chart_template')
        wiz_values = {
             'company_id': company.id,
             'chart_template_id': coa.id,
             'code_digits': 6,
             'update_tax': False,
             'update_account': False,
             'update_fiscal_position': False,
             }
        # We need to run the wizard twice as ormcache is not updated
        # thus taxes are not found
        # Create taxes
        wiz1_values = wiz_values.copy()
        wiz1_values['update_tax'] = True
        wiz1 = cls.env['wizard.update.charts.accounts'].create(wiz1_values)
        wiz1.action_find_records()
        wiz1.action_update_records()

        # Update fiscal positions
        wiz2_values = wiz_values.copy()
        wiz2_values['update_fiscal_position'] = True
        wiz2 = cls.env['wizard.update.charts.accounts'].create(wiz2_values)
        wiz2.action_find_records()
        wiz2.action_update_records()

    @classmethod
    def add_xmlid_fiscal_position(cls):
        fiscal_positions = cls.env['account.fiscal.position'].search([])
        for pos in fiscal_positions:
            if 'APB' in pos.name:
                continue
            elif 'Extra' in pos.name:
                code = 'extra'
            elif 'Intra' in pos.name:
                code = 'intra'
            elif 'National' in pos.name:
                code = 'nat'
            else:
                code = 'cocontractor'

            xmlid = '__setup__.fiscal_position_' + code
            cls.add_xmlid(pos, xmlid)

    @classmethod
    def load_uom(cls):
        with open(INSTALL_CSV_PATH % 'product.uom') as csv_file:
            load_csv(cls.env['product.uom'], csv_file)

    @classmethod
    def load_accounts(cls):
        # set xmlids on existing accounts
        codes = ['400000', '440000', '440100',
                 '550002', '550003', '550004',
                 '550005', '550006', '550007']
        accounts = cls.env['account.account'].search([('code', 'in', codes)])
        imd = cls.env['ir.model.data']
        for acc in accounts:
            name = 'account_%s' % acc.code
            imd.create({
                'name': name,
                'module': '__setup__',
                'model': acc._name,
                'res_id': acc.id,
                'noupdate': True,
            })

        with open(CSV_PATH % 'minimal_account') as csv_file:
            load_csv(cls.env['account.account'], csv_file)
        # Load without change on reconciliation as demo moves exists
        with open(CSV_PATH % 'minimal_account2') as csv_file:
            load_csv(cls.env['account.account'], csv_file)

    @classmethod
    def load_banks(cls):
        with open(INSTALL_CSV_PATH % 'res.bank') as csv_file:
            load_csv(cls.env['res.bank'], csv_file)

    @classmethod
    def load_carriers(cls):
        with open(INSTALL_CSV_PATH % 'delivery.carrier') as csv_file:
            load_csv(cls.env['delivery.carrier'], csv_file)

    @classmethod
    def load_account_journals(cls):
        with open(INSTALL_CSV_PATH % 'account.journal') as csv_file:
            load_csv(cls.env['account.journal'], csv_file)

    @classmethod
    def add_xmlid_journal(cls):
        """ Configure invoicing sequences """
        company = cls.env.ref('base.main_company')
        journals = cls.env['account.journal'].search(
            [('company_id', '=', company.id)]
        )

        customer_journal = journals.filtered(
            lambda a: a.name == 'Customer Invoices'
        )

        imd = cls.env['ir.model.data']
        name = 'account_journal_customer_invoices'
        imd.create({
            'name': name,
            'module': '__setup__',
            'model': customer_journal._name,
            'res_id': customer_journal.id,
            'noupdate': True,
        })

        customer_journal.sequence_id.write({
            'prefix': 'FV/17/',
            'padding': 5,
            'use_date_range': False,
        })

    @classmethod
    def load_account_payment_modes(cls):
        with open(INSTALL_CSV_PATH % 'account.payment.mode') as csv_file:
            load_csv(cls.env['account.payment.mode'], csv_file)

    @classmethod
    def load_account_payment_terms(cls):
        with open(INSTALL_CSV_PATH % 'account.payment.term') as csv_file:
            load_csv(cls.env['account.payment.term'], csv_file)

    @classmethod
    def load_customer_categories(cls):
        with open(INSTALL_CSV_PATH % 'customer.category') as csv_file:
            load_csv(cls.env['res.partner.category'], csv_file)

    @classmethod
    def load_users(cls):
        with open(CSV_PATH % 'res.users') as csv_file:
            load_csv(cls.env['res.users'], csv_file)

    @classmethod
    def load_partner_title(cls):
        with open(INSTALL_CSV_PATH % 'res.partner.title') as csv_file:
            load_csv(cls.env['res.partner.title'], csv_file)

    @classmethod
    def load_suppliers(cls):
        with open(CSV_PATH % 'supplier') as csv_file:
            load_csv(cls.env['res.partner'], csv_file)

    @classmethod
    def load_products(cls):
        with open(CSV_PATH % 'product') as csv_file:
            load_csv(cls.env['product.product'], csv_file)

    @classmethod
    def load_pricelists(cls):
        with open(INSTALL_CSV_PATH % 'product.pricelist') as csv_file:
            load_csv(cls.env['product.pricelist'], csv_file)
        with open(CSV_PATH % 'pricelist_items') as csv_file:
            load_csv(cls.env['product.pricelist.item'], csv_file)

    @classmethod
    def load_customers(cls):
        with open(CSV_PATH % 'customer') as csv_file:
            load_csv(cls.env['res.partner'], csv_file)

    @classmethod
    def create_locations(cls):
        """ Creating stock locations """
        ref = cls.env.ref
        loc_stock = ref('stock.stock_location_stock')
        loc_partner = ref('stock.stock_location_locations_partner')

        # Bins = Products available to pick => under Stock
        locations = [
            ('materiel', 'Matériel',
             loc_stock),
            ('ali', 'Aliments',
             loc_stock),
            ('medoc', 'Médicaments',
             loc_stock),
            ('froid', 'Froid',
             loc_stock),
            ('pharma', 'Pharma',
             loc_partner),
        ]
        Location = cls.env['stock.location'].with_context(
            defer_parent_store_computation=True)
        for xmlid, name, location in locations:
            loc = Location.create({
                'name': name,
                'location_id': location.id,
                'usage': 'view',
            })
            xmlid = '__setup__.stock_location_' + xmlid
            cls.add_xmlid(loc, xmlid)
        Location._parent_store_compute()

    @classmethod
    def setup_warehouse(cls):
        cls.env.ref('stock.warehouse0').delivery_steps = 'pick_ship'

    @classmethod
    def create_picking_types(cls):
        """ Creating picking types """
        ref = cls.env.ref
        wh = ref('stock.warehouse0')
        picking_sequence = wh.pick_type_id.sequence_id

        location_stock = ref('stock.stock_location_stock')
        location_out = ref('stock.stock_location_output')
        location_mat = ref('__setup__.stock_location_materiel')
        location_ali = ref('__setup__.stock_location_ali')
        location_froid = ref('__setup__.stock_location_froid')
        location_pharma = ref('__setup__.stock_location_pharma')

        types = [
            {'xmlid': '__setup__.stock_picking_type_materiel',
             'name': 'Pick Matériel',
             'code': 'internal',
             'sequence_id': picking_sequence.id,
             'default_location_src_id': location_mat.id,
             'default_location_dest_id': location_out.id,
             'use_create_lots': False,
             'subcode': 'PICK',
             'groupbypartner': True,
             'sequence': 6,
             },
            {'xmlid': '__setup__.stock_picking_type_ali',
             'name': 'Pick Aliments',
             'code': 'internal',
             'sequence_id': picking_sequence.id,
             'default_location_src_id': location_ali.id,
             'default_location_dest_id': location_out.id,
             'use_create_lots': False,
             'subcode': 'PICK',
             'groupbypartner': True,
             'sequence': 5,
             'is_portable_printer': True,
             },
            {'xmlid': '__setup__.stock_picking_type_medoc',
             'name': 'Pick Médicaments',
             'code': 'internal',
             'sequence_id': picking_sequence.id,
             'default_location_src_id': location_stock.id,
             'default_location_dest_id': location_out.id,
             'use_create_lots': False,
             'subcode': 'PICK',
             'groupbypartner': True,
             'sequence': 4,
             },
            {'xmlid': '__setup__.stock_picking_type_froid',
             'name': 'Pick Frigo',
             'code': 'internal',
             'sequence_id': picking_sequence.id,
             'default_location_src_id': location_froid.id,
             'default_location_dest_id': location_out.id,
             'use_create_lots': False,
             'subcode': 'PICK',
             'groupbypartner': True,
             'sequence': 7,
             },
            {'xmlid': '__setup__.stock_picking_type_humain',
             'name': 'Pick Humain',
             'code': 'internal',
             'sequence_id': picking_sequence.id,
             'default_location_src_id': location_pharma.id,
             'default_location_dest_id': location_out.id,
             'use_create_lots': False,
             'subcode': 'PICK',
             'groupbypartner': True,
             'sequence': 8,
             },

        ]
        for record in types:
            xmlid = record.pop('xmlid')
            p_type = cls.env['stock.picking.type'].create(record)
            cls.add_xmlid(p_type, xmlid)
        ref('stock.picking_type_internal').active = True
        ref('stock.picking_type_in').write({
            'use_create_lots': False,
            'use_existing_lots': True,
            'subcode': 'RECEIVE',
            'default_location_dest_id': ref(
                'stock.stock_location_company').id
        })

    @classmethod
    def create_procurement_rules(cls):
        """ Creating procurement rules """
        ref = cls.env.ref
        location_out = ref('stock.stock_location_output')
        warehouse = cls.env.ref('stock.warehouse0')
        rules = [
            {'xmlid': '__setup__.procurement_rule_materiel',
             'type': ['categ', 'prod'],
             'name': 'WH: Stock -> Output (MAT)',
             'action': 'move',
             'location_id': location_out.id,
             'warehouse_id': warehouse.id,
             'location_src_id': ref('stock.stock_location_stock').id,
             'procure_method': 'make_to_stock',
             'picking_type_id': ref(
                 '__setup__.stock_picking_type_materiel').id,
             'group_propagation_option': 'propagate',
             },
            {'xmlid': '__setup__.procurement_rule_ali',
             'type': ['categ', 'prod'],
             'name': 'WH: Stock -> Output (ALI)',
             'action': 'move',
             'location_id': location_out.id,
             'warehouse_id': warehouse.id,
             'location_src_id': ref('stock.stock_location_stock').id,
             'procure_method': 'make_to_stock',
             'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
             'group_propagation_option': 'propagate',
             },
            {'xmlid': '__setup__.procurement_rule_medoc',
             'type': ['categ', 'prod'],
             'name': 'WH: Stock -> Output (MED)',
             'action': 'move',
             'location_id': location_out.id,
             'warehouse_id': warehouse.id,
             'location_src_id': ref('stock.stock_location_stock').id,
             'procure_method': 'make_to_stock',
             'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
             'group_propagation_option': 'propagate',
             },
            {'xmlid': '__setup__.procurement_rule_froid',
             'type': ['prod'],
             'name': 'WH: Stock -> Output (FRIGO)',
             'action': 'move',
             'location_id': location_out.id,
             'warehouse_id': warehouse.id,
             'location_src_id': ref('stock.stock_location_stock').id,
             'procure_method': 'make_to_stock',
             'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
             'group_propagation_option': 'propagate',
             },
        ]
        for record in rules:
            base_xmlid = record.pop('xmlid')
            types = record.pop('type')
            sequences = {'categ': 15, 'prod': 10}
            for t in types:
                record['sequence'] = sequences[t]
                rule = cls.env['procurement.rule'].create(record)
                xmlid = '%s_%s' % (base_xmlid, t)
                cls.add_xmlid(rule, xmlid)

    @classmethod
    def create_routes(cls):
        """ Creating routes """
        ref = cls.env.ref
        routes = [
            {'xmlid': '__setup__.stock_location_route_pick_materiel_categ',
             'name': 'Zone Matériel (Categ)',
             'pull_ids': [
                 (6, 0, ref('__setup__.procurement_rule_materiel_categ').ids)],
             'product_categ_selectable': True,
             'product_selectable': False,
             },
            {'xmlid': '__setup__.stock_location_route_pick_materiel',
             'name': 'Zone Matériel',
             'pull_ids': [
                 (6, 0, ref('__setup__.procurement_rule_materiel_prod').ids)],
             'product_categ_selectable': False,
             'product_selectable': True,
             },

            {'xmlid': '__setup__.stock_location_route_pick_ali_categ',
             'name': 'Zone Aliments (Categ)',
             'pull_ids': [
                 (6, 0, ref('__setup__.procurement_rule_ali_categ').ids)],
             'product_categ_selectable': True,
             'product_selectable': False,
             },
            {'xmlid': '__setup__.stock_location_route_pick_ali',
             'name': 'Zone Aliments',
             'pull_ids': [
                 (6, 0, ref('__setup__.procurement_rule_ali_prod').ids)],
             'product_categ_selectable': False,
             'product_selectable': True,
             },

            {'xmlid': '__setup__.stock_location_route_pick_medoc',
             'name': 'Zone Médicaments',
             'pull_ids': [
                 (6, 0, ref('__setup__.procurement_rule_medoc_prod').ids)],
             'product_categ_selectable': False,
             'product_selectable': True,
             },

            {'xmlid': '__setup__.stock_location_route_pick_froid',
             'name': 'Zone FROID / FRIGO',
             'pull_ids': [
                 (6, 0, ref('__setup__.procurement_rule_froid_prod').ids)],
             'product_selectable': True,
             },

        ]
        for record in routes:
            xmlid = record.pop('xmlid')
            record['sequence'] = 20
            route = cls.env['stock.location.route'].create(record)
            cls.add_xmlid(route, xmlid)
