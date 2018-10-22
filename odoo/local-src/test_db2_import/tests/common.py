# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from contextlib import contextmanager

import csv
import mock
from os import path

from odoo.tests.common import SavepointCase


# Cols name and type created quickly with \d and replacing types

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
 "dccre  VARCHAR,"
 "deleted BOOLEAN")

PO_COLS = (
 "ecfctr VARCHAR,"
 "ecfsui INTEGER,"
 "ecfuti INTEGER,"
 "ecftyc INTEGER,"
 "ecfsuc VARCHAR,"
 "ecfssu VARCHAR,"
 "ecfdss INTEGER,"
 "ecfdaa INTEGER,"
 "ecfdmm INTEGER,"
 "ecfdjj INTEGER,"
 "ecfdiv DOUBLE PRECISION,"
 "ecffou DOUBLE PRECISION,"
 "ecfrin VARCHAR,"
 "ecfrcl VARCHAR,"
 "ecflss INTEGER,"
 "ecflaa INTEGER,"
 "ecflmm INTEGER,"
 "ecfljj INTEGER,"
 "ecfmdl INTEGER,"
 "ecfrem DOUBLE PRECISION,"
 "ecfrms DOUBLE PRECISION,"
 "ecfdev DOUBLE PRECISION,"
 "ecftau DOUBLE PRECISION,"
 "ecfdel INTEGER,"
 "ecfnal INTEGER,"
 "ecfqua DOUBLE PRECISION,"
 "ecfed1 DOUBLE PRECISION,"
 "ecfcom DOUBLE PRECISION,"
 "ecfedc DOUBLE PRECISION,"
 "ecfncd DOUBLE PRECISION,"
 "ecfjes DOUBLE PRECISION,"
 "ecftes DOUBLE PRECISION,"
 "ecfnof VARCHAR,"
 "ecffss INTEGER,"
 "ecffaa INTEGER,"
 "ecffmm INTEGER,"
 "ecffjj INTEGER,"
 "ecfcss INTEGER,"
 "ecfcaa INTEGER,"
 "ecfcmm INTEGER,"
 "ecfcjj INTEGER,"
 "ecfmss INTEGER,"
 "ecfmaa INTEGER,"
 "ecfmmm INTEGER,"
 "ecfmjj INTEGER,"
 "ecfpss INTEGER,"
 "ecfpaa INTEGER,"
 "ecfpmm INTEGER,"
 "ecfpjj INTEGER,"
 "ecfana VARCHAR,"
 "ecfdnl DOUBLE PRECISION,"
 "ecfmto DOUBLE PRECISION,"
 "ecfsts DOUBLE PRECISION,"
 "ecfres VARCHAR")

POL_COLS = (
 "dcfctr VARCHAR,"
 "dcfsui INTEGER,"
 "dcfuti INTEGER,"
 "dcfnli DOUBLE PRECISION,"
 "dcfsuc VARCHAR,"
 "dcfssu VARCHAR,"
 "dcffou DOUBLE PRECISION,"
 "dcfcli DOUBLE PRECISION,"
 "dcfart VARCHAR,"
 "dcflib VARCHAR,"
 "dcfquc DOUBLE PRECISION,"
 "dcfqur DOUBLE PRECISION,"
 "dcfqul DOUBLE PRECISION,"
 "dcflss INTEGER,"
 "dcflaa INTEGER,"
 "dcflmm INTEGER,"
 "dcfljj INTEGER,"
 "dcfpac DOUBLE PRECISION,"
 "dcfprv DOUBLE PRECISION,"
 "dcfrem DOUBLE PRECISION,"
 "dcfres DOUBLE PRECISION,"
 "dcfunv DOUBLE PRECISION,"
 "dcfgro DOUBLE PRECISION,"
 "dcfsgr DOUBLE PRECISION,"
 "dcfcva DOUBLE PRECISION,"
 "dcfcan DOUBLE PRECISION,"
 "dcfsta DOUBLE PRECISION,"
 "dcfstb DOUBLE PRECISION,"
 "dcfstc DOUBLE PRECISION,"
 "dcfstf DOUBLE PRECISION,"
 "dcfpsp DOUBLE PRECISION,"
 "dcfnfa VARCHAR,"
 "dcffss INTEGER,"
 "dcffaa INTEGER,"
 "dcffmm INTEGER,"
 "dcffjj INTEGER,"
 "dcfcss INTEGER,"
 "dcfcaa INTEGER,"
 "dcfcmm INTEGER,"
 "dcfcjj INTEGER,"
 "dcfmss INTEGER,"
 "dcfmaa INTEGER,"
 "dcfmmm INTEGER,"
 "dcfmjj INTEGER,"
 "dcfre  VARCHAR,"
 "deleted BOOLEAN")

DRECEP_COLS = (
 "drpsuc VARCHAR,"
 "drpctr VARCHAR,"
 "drpsui INTEGER,"
 "drpnfa VARCHAR,"
 "drpdat INTEGER,"
 "drpnli INTEGER,"
 "drpnfo INTEGER,"
 "drpseq INTEGER,"
 "drpart VARCHAR,"
 "drpdem VARCHAR,"
 "drplot VARCHAR,"
 "drpdpr INTEGER,"
 "drpqtn INTEGER,"
 "drpqre INTEGER,"
 "drpqra INTEGER,"
 "drpqrf INTEGER,"
 "drpgng INTEGER,"
 "drpprb VARCHAR,"
 "drplll INTEGER,"
 "drpscp INTEGER,"
 "drpscd INTEGER,"
 "drpeap INTEGER,"
 "drpead INTEGER,"
 "drpara VARCHAR,"
 "drpora INTEGER,"
 "drporf INTEGER,"
 "drpong INTEGER,"
 "drpapr VARCHAR,"
 "drpsta INTEGER,"
 "drpstb INTEGER,"
 "drpstc INTEGER,"
 "drpstf INTEGER")


HISPRB_COLS = (
 "hpbsuc VARCHAR,"
 "hpbctr VARCHAR,"
 "hpbsui DOUBLE PRECISION,"
 "hpbnli DOUBLE PRECISION,"
 "hpbnfo DOUBLE PRECISION,"
 "hpbnfa VARCHAR,"
 "hpbdat DOUBLE PRECISION,"
 "hpbcpb VARCHAR,"
 "hpbccd VARCHAR,"
 "hpbccl VARCHAR,"
 "hpbde1 VARCHAR,"
 "hpbde2 VARCHAR,"
 "hpbde3 VARCHAR,"
 "hpbde4 VARCHAR,"
 "hpbde5 VARCHAR,"
 "hpbaus VARCHAR,"
 "hpbada DOUBLE PRECISION,"
 "hpbsid VARCHAR,"
 "hpbsda DOUBLE PRECISION,"
 "hpbsco VARCHAR,"
 "hpblll DOUBLE PRECISION")


HISSPR_COLS = (
 "hpssuc VARCHAR,"
 "hpsctr VARCHAR,"
 "hpssui DOUBLE PRECISION,"
 "hpsnli DOUBLE PRECISION,"
 "hpssli DOUBLE PRECISION,"
 "hpsnfo DOUBLE PRECISION,"
 "hpsnfa VARCHAR,"
 "hpsdat DOUBLE PRECISION,"
 "hpscpb VARCHAR,"
 "hpsccd VARCHAR,"
 "hpsccl VARCHAR,"
 "hpssid VARCHAR,"
 "hpssda DOUBLE PRECISION,"
 "hpssco VARCHAR,"
 "hpssts VARCHAR")

SQL_PATH = path.join(path.dirname(__file__), "sql", "%s.sql")
CSV_PATH = path.join(path.dirname(__file__), "data", "%s.csv")

# Don't copy files of this project
# Quite ugly but this avoid to copy the files in the project
# we need some of those data in the tests
INSTALL_CSV_PATH = path.join("/odoo/data/install", "%s.csv")


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


def create_or_update(cls, model, xmlid, values):
    """ doppleganger of create_or_update from anthem """
    rec = cls.env.ref(xmlid, raise_if_not_found=False)
    if rec:
        rec.write(values)
    else:
        if isinstance(model, str):
            Model = cls.env[model]
        else:
            Model = model
        res = Model.create(values)
        cls.add_xmlid(res, xmlid)


class DB2ImportTestCase(SavepointCase):

    @contextmanager
    def mock_with_delay(self):
        with mock.patch('odoo.addons.queue_job.models.base.DelayableRecordset',
                        name='DelayableRecordset', spec=True
                        ) as delayable_cls:
            # prepare the mocks
            delayable = mock.MagicMock(name='DelayableBinding')
            delayable_cls.return_value = delayable
            yield delayable_cls, delayable

    @classmethod
    def setUpClass(cls):
        super(DB2ImportTestCase, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context,
                          tracking_disable=True))

        cls.create_db2_tables()
        cls.insert_db2_records()
        cls.load_uom()
        cls.load_legal_entities()
        cls.update_chart_of_account()
        cls.add_xmlid_fiscal_position()
        cls.load_accounts()
        cls.load_banks()
        cls.load_carriers()
        cls.load_account_journals()
        cls.add_xmlid_journal()
        cls.load_account_payment_methods()
        cls.load_account_payment_modes()
        cls.load_account_payment_terms()
        cls.load_users()
        cls.load_partner_title()
        cls.load_suppliers()
        cls.create_locations()
        cls.setup_warehouse()
        cls.create_picking_zones()
        cls.create_picking_types()
        cls.configure_procurement_rules()
        cls.create_procurement_rules()
        cls.create_procurement_rules_mto()
        cls.create_procurement_rules_mto_mts()
        cls.create_routes()
        cls.assign_route_categories()
        cls.set_picking_zone()
        cls.set_product_expiry()
        cls.load_products()
        cls.load_supplierinfo()
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
        """Create tables to use in tests.
        """

        ref = cls.env.ref

        db2_so_table = ref('db2_import.db2_table_pentcdcl_for_sale')
        db2_sol_table = ref('db2_import.db2_table_pdetcdcl_for_sale')

        db2_so_table._create_db2_table(SO_COLS)
        db2_sol_table._create_db2_table(SOL_COLS)

        db2_po_table = ref('db2_import.db2_table_pentcdfo_for_purchase')
        db2_pol_table = ref('db2_import.db2_table_pdetcdfo_for_purchase')

        db2_po_table._create_db2_table(PO_COLS)
        db2_pol_table._create_db2_table(POL_COLS)

    @classmethod
    def insert_db2_records(cls):
        """Insert records to use in tests."""
        cr = cls.env.cr
        for table in ['db2_pentcdcl', 'db2_pdetcdcl',
                      'db2_pentcdfo', 'db2_pdetcdfo',
                      'db2_drecep', 'db2_hisprb', 'db2_hisspr']:
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
    def load_legal_entities(cls):
        with open(INSTALL_CSV_PATH % 'legal.entity') as csv_file:
            load_csv(cls.env['legal.entity'], csv_file)

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
        Carrier = cls.env['delivery.carrier'].with_context(
            tracking_disable=True,
            no_connector_export=True,
            force_archive_orderpoint=True
        )
        with open(INSTALL_CSV_PATH % 'delivery.carrier') as csv_file:
            load_csv(Carrier, csv_file)

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
    def load_account_payment_methods(cls):
        with open(INSTALL_CSV_PATH % 'account.payment.method') as csv_file:
            load_csv(cls.env['account.payment.method'], csv_file)

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
        User = cls.env['res.users'].with_context(
            no_reset_password=True,
            tracking_disable=True,
        )
        with open(CSV_PATH % 'res.users') as csv_file:
            load_csv(User, csv_file)

    @classmethod
    def load_partner_title(cls):
        with open(INSTALL_CSV_PATH % 'res.partner.title') as csv_file:
            load_csv(cls.env['res.partner.title'], csv_file)

    @classmethod
    def load_suppliers(cls):
        Partner = cls.env['res.partner'].with_context(
            tracking_disable=True
        )
        with open(CSV_PATH % 'supplier') as csv_file:
            load_csv(Partner, csv_file)

    @classmethod
    def load_products(cls):
        Product = cls.env['product.product'].with_context(
            tracking_disable=True,
            no_connector_export=True,
            force_archive_orderpoint=True
        )
        with open(CSV_PATH % 'product') as csv_file:
            load_csv(Product, csv_file)
        with open(CSV_PATH % 'additional_product') as csv_file:
            load_csv(Product, csv_file)

    @classmethod
    def load_supplierinfo(cls):
        with open(CSV_PATH % 'supplierinfo_promo') as csv_file:
            load_csv(cls.env['product.supplierinfo'], csv_file)

    @classmethod
    def load_pricelists(cls):
        with open(INSTALL_CSV_PATH % 'product.pricelist') as csv_file:
            load_csv(cls.env['product.pricelist'], csv_file)
        with open(CSV_PATH % 'pricelist_items') as csv_file:
            load_csv(cls.env['product.pricelist.item'], csv_file)

    @classmethod
    def load_customers(cls):
        Partner = cls.env['res.partner'].with_context(
            tracking_disable=True
        )
        with open(CSV_PATH % 'customer') as csv_file:
            load_csv(Partner, csv_file)

    @classmethod
    def create_locations(cls):
        """ Creating stock locations """
        ref = cls.env.ref
        loc_stock = ref('stock.stock_location_stock')
        loc_partner = ref('stock.stock_location_locations_partner')

        Location = cls.env['stock.location'].with_context(
                    defer_parent_store_computation='manually')

        # Reserves = Products available => under WH, above Stock
        reserves = [
            ('reserve_ali', 'Réserve Aliments',
             loc_stock.location_id),
            ('reserve_medoc', 'Réserve Médicaments',
             loc_stock.location_id),
        ]
        for xmlid, name, location in reserves:
            loc = Location.create({
                'name': name,
                'location_id': location.id,
                'usage': 'view',
                'kind': 'reserve',
            })
            xmlid = '__setup__.stock_location_' + xmlid
            cls.add_xmlid(loc, xmlid)

        ('__setup__.stock_location_materiel', 'Matériel',
         loc_stock.id),
        ('__setup__.stock_location_ali', 'Aliments',
         loc_stock.id),
        ('__setup__.stock_location_medoc', 'Médicaments',
         loc_stock.id),
        ('__setup__.stock_location_froid', 'Froid',
         False,
         loc_stock.id),
        # Bins = Products available to pick => under Stock
        locations = [
            ('materiel', 'Matériel',
             False,
             loc_stock, ),
            ('ali', 'Aliments',
             ref('__setup__.stock_location_reserve_ali'),
             loc_stock),
            ('medoc', 'Médicaments',
             ref('__setup__.stock_location_reserve_medoc'),
             loc_stock),
            ('froid', 'Froid',
             False,
             loc_stock),
        ]
        for xmlid, name, reserve, location in locations:
            loc = Location.create({
                'name': name,
                'location_id': location.id,
                'usage': 'view',
                'reserve_location_id': reserve and reserve.id,
            })
            xmlid = '__setup__.stock_location_' + xmlid
            cls.add_xmlid(loc, xmlid)
        locations = [
            ('__setup__.stock_location_frigo', 'Frigo',
             False,
             ref('__setup__.stock_location_froid').id),
        ]
        for xmlid, name, reserve_id, location_id in locations:
            create_or_update(cls, Location, xmlid, {
                'name': name,
                'location_id': location_id,
                'reserve_location_id': reserve_id,
                'usage': 'view',
            })

        # Parking is under Input (part of stock)
        parkings = [
            (
                '__setup__.stock_location_parking_medoc',
                'Parking Medicaments',
            ),
            (
                '__setup__.stock_location_parking_ali',
                'Parking Aliments',
            ),
            (
                '__setup__.stock_location_parking_materiel',
                'Parking Matériel',
            ),
            (
                '__setup__.stock_location_parking_frigo',
                'Parking Frigo',
            ),
        ]
        for xmlid, name in parkings:
            create_or_update(cls, Location, xmlid, {
                'name': name,
                'location_id': ref('stock.stock_location_company').id,
                'usage': 'view',
                'kind': 'parking',
            })

        # Achetés-Vendus is under Input (part of stock)
        create_or_update(
            cls, Location, '__setup__.stock_location_onorder',
            {
                'name': 'Achetés-Vendus',
                'location_id': ref('stock.stock_location_company').id,
                'usage': 'view',
            })
        onorders = [
            ('__setup__.stock_location_order_ali', 'Achetés-Vendus Aliments'),
            ('__setup__.stock_location_order_medoc',
             'Achetés-Vendus Médicaments'),
            ('__setup__.stock_location_order_frigo', 'Achetés-Vendus Frigo'),
            ('__setup__.stock_location_order_mat', 'Achetés-Vendus Matériel'),
        ]
        for xmlid, name in onorders:
            create_or_update(cls, Location, xmlid, {
                'name': name,
                'location_id': ref('__setup__.stock_location_onorder').id,
                'usage': 'view',
            })

        # Nouveautés is under Input (part of stock)
        create_or_update(
            cls, Location, '__setup__.stock_location_new',
            {
                'name': 'Nouveautés',
                'location_id': ref('stock.stock_location_company').id,
                'usage': 'view',
            })
        news = [
            ('__setup__.stock_location_new_ali', 'Nouveautés Aliments'),
            ('__setup__.stock_location_new_medoc', 'Nouveautés Médicaments'),
            ('__setup__.stock_location_new_frigo', 'Nouveautés Frigo'),
            ('__setup__.stock_location_new_mat', 'Nouveautés Matériel'),
        ]
        for xmlid, name in news:
            create_or_update(cls, Location, xmlid, {
                'name': name,
                'location_id': ref('__setup__.stock_location_new').id,
                'usage': 'view',
            })

        # Casse = Products unavailable => not under physical locations
        create_or_update(
            cls, Location, 'stock.stock_location_scrapped', {
                'name': 'Scrap',
                'location_id': False,
                'usage': 'view',
                'scrap_location': False,
            })
        scrap = [
            ('__setup__.stock_location_scrap_destroy', 'A détruire', 0, 0),
            ('__setup__.stock_location_scrap_quality',
             'Problème Qualité', 0, 1),
            ('__setup__.stock_location_scrap_return',
             'Retours Fournisseur', 1, 0),
            ]
        for xmlid, name, accrued_supplier_return, is_scrap in scrap:
            create_or_update(cls, Location, xmlid, {
                'name': name,
                'location_id': ref('stock.stock_location_scrapped').id,
                'usage': 'internal',
                'ignore_quants_expiration': True,
                'scrap_location': is_scrap,
                'accrued_supplier_return': accrued_supplier_return,
            })

        loc_partner = ref('stock.stock_location_locations_partner')
        create_or_update(
            cls, Location, '__setup__.stock_location_destroyed', {
                'name': 'Détruit',
                'location_id': loc_partner.id,
                'usage': 'customer',
            })
        # Create a location for migrated Sales
        loc = Location.create({
            'name': '[MIGRATION] Stock ventes',
            'usage': 'customer',
            'active': True,
        })
        xmlid = '__setup__.mig_sale_pick'
        cls.add_xmlid(loc, xmlid)
        Location._parent_store_compute()

        # Create a location for migrated Purchases
        loc = Location.create({
            'name': '[MIGRATION] Réception achats',
            'usage': 'supplier',
            'active': True,
        })
        xmlid = '__setup__.mig_purchase_reception'
        cls.add_xmlid(loc, xmlid)
        Location._parent_store_compute()

    @classmethod
    def setup_warehouse(cls):
        cls.env.ref('stock.warehouse0').delivery_steps = 'pick_ship'

    @classmethod
    def create_picking_zones(cls):
        """ Creating picking zones """
        with open(INSTALL_CSV_PATH % 'picking.zone') as csv_file:
            load_csv(cls.env['picking.zone'], csv_file)

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

        color_mrp = 0
        color_in = 1
        color_internal = 4
        color_pick = 5
        color_out = 8

        types = [
            {'xmlid': 'stock.picking_type_in',
             'name': u'Réception des achats',
             'use_create_lots': False,
             'use_existing_lots': True,
             'subcode': 'RECEIVE',
             'color': color_in,
             'sequence': 10,
             },
            {'xmlid': 'stock.picking_type_internal',
             'active': True,
             'sequence': 50,
             'color': color_internal,
             },

            {'xmlid': '__setup__.stock_picking_type_materiel',
             'name': 'Pick Matériel',
             'code': 'internal',
             'sequence_id': picking_sequence.id,
             'default_location_src_id': location_mat.id,
             'default_location_dest_id': location_out.id,
             'use_create_lots': False,
             'subcode': 'PICK',
             'groupbypartner': True,
             'color': color_pick,
             'sequence': 60,
             'picking_zone_id': ref('__setup__.picking_zone_materiel').id,
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
             'color': color_pick,
             'sequence': 61,
             'picking_zone_id': ref('__setup__.picking_zone_aliments').id,
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
             'color': color_pick,
             'sequence': 62,
             'picking_zone_id': ref(
                 '__setup__.picking_zone_medicament').id,
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
             'color': color_pick,
             'sequence': 63,
             'picking_zone_id': ref('__setup__.picking_zone_frigo').id,
             },
            {'xmlid': 'stock.picking_type_out',
             'active': True,
             'color': color_out,
             'sequence': 90,
             },
        ]
        for record in types:
            xmlid = record.pop('xmlid')
            create_or_update(cls, cls.env['stock.picking.type'], xmlid, record)

        ref('stock.picking_type_in').write({
            'default_location_dest_id': ref(
                'stock.stock_location_company').id
        })
        cls.env['stock.picking.type'].search([('name', '=', 'Pick')]).write({
            'subcode': 'PICK',
            'sequence': 59,
            'color': color_pick,
            })
        cls.env['stock.picking.type'].search([('code', '=', 'mrp_operation')])\
            .write({
                'sequence': 89,
                'color': color_mrp,
                })

    @classmethod
    def configure_procurement_rules(cls):
        """
        Change the procurement location (VLB Stock -> VLB) for the BUY rules
        """
        location_vlb_stock = cls.env.ref('stock.stock_location_stock')
        # The location VLB doesn't have a XML ID
        location_vlb = location_vlb_stock.location_id

        rulesBuy = cls.env['procurement.rule'].search([('action', '=', 'buy')])
        rulesBuy.write({
            'location_id': location_vlb.id
        })

    @classmethod
    def create_procurement_rules(cls):
        """ Creating procurement rules """
        ref = cls.env.ref
        location_out = ref('stock.stock_location_output')
        warehouse = cls.env.ref('stock.warehouse0')
        rules = [
            {'xmlid': '__setup__.procurement_rule_materiel',
             'type': ['categ', 'prod', 'sale'],
             'name': 'WH: Stock -> Output (MAT)',
             'picking_type_id': ref(
                 '__setup__.stock_picking_type_materiel').id,
             },
            {'xmlid': '__setup__.procurement_rule_ali',
             'type': ['categ', 'prod', 'sale'],
             'name': 'WH: Stock -> Output (ALI)',
             'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
             },
            {'xmlid': '__setup__.procurement_rule_medoc',
             'type': ['categ', 'prod', 'sale'],
             'name': 'WH: Stock -> Output (MED)',
             'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
             },
            {'xmlid': '__setup__.procurement_rule_froid',
             'type': ['prod', 'sale'],
             'name': 'WH: Stock -> Output (FRIGO)',
             'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
             },
        ]
        for record in rules:
            base_xmlid = record.pop('xmlid')
            types = record.pop('type')
            default_name = record.pop('name')
            record.update({
             'action': 'move',
             'location_id': location_out.id,
             'warehouse_id': warehouse.id,
             'procure_method': 'make_to_stock',
             'group_propagation_option': 'propagate',
            })
            sequences = {'categ': 15, 'prod': 10, 'sale': 0}
            for t in types:
                xmlid = base_xmlid + '_' + t
                if t == 'sale':
                    record['location_src_id'] = ref(
                        'stock.stock_location_company').id
                else:
                    record['location_src_id'] = ref(
                        'stock.stock_location_stock').id
                record['name'] = default_name[:-1] + " - " + t.upper() + ")"
                record['sequence'] = sequences[t]
                create_or_update(cls, cls.env['procurement.rule'],
                                 xmlid, record)

    @classmethod
    def create_procurement_rules_mto(cls):
        """ Creating procurement rules MTO """

        # delete existing procurement rule for MTO
        rule = cls.env['procurement.rule'].search(
            [('name', '=', 'WH: Stock -> OutputMTO')])
        rule.unlink()

        ref = cls.env.ref
        location_out = ref('stock.stock_location_output')
        warehouse = cls.env.ref('stock.warehouse0')
        types = [{
            'xmlid': '__setup__.procurement_rule_materiel_mto',
            'name': 'WH: Stock -> Output MTO (MAT)',
            'action': 'move',
            'sequence': 25,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_order',
            'picking_type_id': ref('__setup__.stock_picking_type_materiel').id,
            'group_propagation_option': 'propagate',
        }, {
            'xmlid': '__setup__.procurement_rule_ali_mto',
            'name': 'WH: Stock -> Output MTO (ALI)',
            'action': 'move',
            'sequence': 25,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_order',
            'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
            'group_propagation_option': 'propagate',
        }, {
            'xmlid': '__setup__.procurement_rule_medoc_mto',
            'name': 'WH: Stock -> Output MTO (MED)',
            'action': 'move',
            'sequence': 25,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_order',
            'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
            'group_propagation_option': 'propagate',
        }, {
            'xmlid': '__setup__.procurement_rule_froid_mto',
            'name': 'WH: Stock -> Output MTO (FRIGO)',
            'action': 'move',
            'sequence': 25,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_order',
            'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
            'group_propagation_option': 'propagate',
        }]
        for record in types:
            xmlid = record.pop('xmlid')
            rule = cls.env['procurement.rule'].create(record)
            cls.add_xmlid(rule, xmlid)

    @classmethod
    def create_procurement_rules_mto_mts(cls):
        """ Creating procurement rules MTO+MTS """
        ref = cls.env.ref
        location_out = ref('stock.stock_location_output')
        warehouse = ref('stock.warehouse0')
        types = [{
            'xmlid': '__setup__.procurement_rule_materiel_mto_mtu',
            'name': 'WH: Stock -> Output MTO+MTS (MAT)',
            # for data import, consider those rules as MTS only
            # 'action': 'split_procurement',
            'action': 'move',
            'sequence': 30,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_stock',
            'picking_type_id': ref('__setup__.stock_picking_type_materiel').id,
            'group_propagation_option': 'propagate',
            'mts_rule_id':
                ref('__setup__.procurement_rule_materiel_prod').id,
            'mto_rule_id':
                ref('__setup__.procurement_rule_materiel_mto').id,
        }, {
            'xmlid': '__setup__.procurement_rule_ali_mto_mtu',
            'name': 'WH: Stock -> Output MTO+MTS (ALI)',
            # for data import, consider those rules as MTS only
            # 'action': 'split_procurement',
            'action': 'move',
            'sequence': 30,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_stock',
            'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
            'group_propagation_option': 'propagate',
            'mts_rule_id': ref('__setup__.procurement_rule_ali_prod').id,
            'mto_rule_id': ref('__setup__.procurement_rule_ali_mto').id,
        }, {
            'xmlid': '__setup__.procurement_rule_medoc_mto_mtu',
            'name': 'WH: Stock -> Output MTO+MTS (MED)',
            # for data import, consider those rules as MTS only
            # 'action': 'split_procurement',
            'action': 'move',
            'sequence': 30,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_stock',
            'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
            'group_propagation_option': 'propagate',
            'mts_rule_id':
                ref('__setup__.procurement_rule_medoc_prod').id,
            'mto_rule_id': ref('__setup__.procurement_rule_medoc_mto').id,
        }, {
            'xmlid': '__setup__.procurement_rule_froid_mto_mtu',
            'name': 'WH: Stock -> Output MTO+MTS (FRIGO)',
            # for data import, consider those rules as MTS only
            # 'action': 'split_procurement',
            'action': 'move',
            'sequence': 30,
            'location_id': location_out.id,
            'warehouse_id': warehouse.id,
            'location_src_id': ref('stock.stock_location_stock').id,
            'procure_method': 'make_to_stock',
            'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
            'group_propagation_option': 'propagate',
            'mts_rule_id':
                ref('__setup__.procurement_rule_froid_prod').id,
            'mto_rule_id': ref('__setup__.procurement_rule_froid_mto').id,
        }]
        for record in types:
            xmlid = record.pop('xmlid')
            create_or_update(cls, cls.env['procurement.rule'], xmlid, record)

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

            {'xmlid': '__setup__.stock_location_route_pick_medoc_categ',
             'name': 'Zone Médicaments (Categ)',
             'pull_ids': [
                 (6, 0, ref('__setup__.procurement_rule_medoc_categ').ids)],
             'product_categ_selectable': True,
             'product_selectable': False,
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

            {'xmlid': '__setup__.stock_location_route_new',
             'name': 'Nouveauté',
             'product_categ_selectable': False,
             'product_selectable': True,
             },
        ]
        for record in routes:
            xmlid = record.pop('xmlid')
            record['sequence'] = 20
            route = cls.env['stock.location.route'].create(record)
            cls.add_xmlid(route, xmlid)

        route_mto_values = {
            'pull_ids': [
                (6, 0, [ref('__setup__.procurement_rule_materiel_mto_mtu').id,
                        ref('__setup__.procurement_rule_ali_mto_mtu').id,
                        ref('__setup__.procurement_rule_medoc_mto_mtu').id,
                        ref('__setup__.procurement_rule_froid_mto_mtu').id])
            ]
        }

        route_mto = ref('stock.route_warehouse0_mto')
        route_mto.write(route_mto_values)

        # Disable the route MTO+MTS
        route_mto_mts = ref('stock_mts_mto_rule.route_mto_mts')
        route_mto_mts.write({'product_selectable': False})

        # Create Sales BO route
        cls.env['stock.location.route'].create({
            'name': 'BO',
            'sequence': 0,
            'priority': 0,
            'product_categ_selectable': False,
            'product_selectable': False,
            'sale_selectable': True,
            'pull_ids': [
                (6, 0, [ref('__setup__.procurement_rule_ali_sale').id,
                        ref('__setup__.procurement_rule_medoc_sale').id,
                        ref('__setup__.procurement_rule_materiel_sale').id,
                        ref('__setup__.procurement_rule_froid_sale').id])],
        })

    @classmethod
    def assign_route_categories(cls):
        """ Assigning routes to product categories """
        ref = cls.env.ref
        categs = [('specific_data.product_categ_materiel',
                   '__setup__.stock_location_route_pick_materiel_categ'),
                  ('specific_data.product_categ_ali',
                   '__setup__.stock_location_route_pick_ali_categ'),
                  ('specific_data.product_categ_medoc',
                   '__setup__.stock_location_route_pick_medoc_categ'),
                  ]
        for category_xmlid, route_xmlid in categs:
            ref(category_xmlid).route_ids = [(6, 0, ref(route_xmlid).ids)]

    @classmethod
    def set_picking_zone(cls):
        """
        Set the picking zone on all picking locations and on products
        """
        main_locations_picking_zone_mapping = {
            'ali': '__setup__.picking_zone_aliments',
            'froid': '__setup__.picking_zone_frigo',
            'materiel': '__setup__.picking_zone_materiel',
            'medoc': '__setup__.picking_zone_medicament',
        }
        base_xmlid = '__setup__.stock_location_'
        for main_location_xmlid, picking_zone_xmlid in \
                main_locations_picking_zone_mapping.iteritems():
            main_location_xmlid = base_xmlid + main_location_xmlid
            main_location = cls.env.ref(main_location_xmlid)
            picking_zone_id = cls.env.ref(picking_zone_xmlid)
            children = cls.env['stock.location'].search([
                ('id', 'child_of', main_location.id)])
            (main_location | children).write({
                'picking_zone_id': picking_zone_id.id
            })

        # Recompute the picking zone on each products
        cls.env['product.template'].search([])._compute_picking_zone_id()

    @classmethod
    def set_product_expiry(cls):
        """ Set the expiry delay on product categories """
        cls.env['product.category'].search([]).write({
            'alert_time': 1,
            'removal_time': 91,
            'life_time': 121,
            })

    def check_values(self, record, expected_values):
        for k, expect in expected_values.iteritems():
            if expect is False:
                self.assertFalse(record[k],
                                 msg="Field %s must be false in %s"
                                 % (k, record.name))
            elif isinstance(expect, float):
                self.assertAlmostEqual(record[k], expect,
                                       msg="Wrong value on field %s in %s"
                                       % (k, record.name))
            else:
                self.assertEqual(record[k], expect,
                                 msg="Wrong value on field %s in %s"
                                 % (k, record.name))
