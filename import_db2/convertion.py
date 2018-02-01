# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import OrderedDict
import re

from base import EntityMapper, FieldMapper
from datetime import datetime
import checks
import mappings

from mapper import const, ref, concat, call

# Sample data for 100 SO
SO_MIN = 2691678
SO_MAX = 2691777


class ProductMapper(EntityMapper):
    DB2_NAME = 'PGESTION'

    XMLID_FIELD = 'default_code'

    FIELDS_MAPPING = [
        FieldMapper('default_code', 'gesart'),
        FieldMapper('list_price', 'gespvr'),
        FieldMapper('standard_price', 'gespan'),
        FieldMapper(
            'indicated_price', 'cplz23',
        ),
        FieldMapper('sale_delay', constant=0),
        FieldMapper('weight', 'gespbr'),
        FieldMapper(
            'uom_po_id/id', 'gesuna',
            mapping=mappings.UOM, default='product.product_uom_unit'
        ),
        FieldMapper(
            'uom_id/id', 'gesunv',
            mapping=mappings.UOM, default='product.product_uom_unit'
        ),
        FieldMapper('medical_device', 'cplz20', mapping=mappings.STR_BOOL),
        FieldMapper('cnk_code', 'cplz03'),
        FieldMapper(
            'web_published', 'cplz19',
            mapping=mappings.PRODUCT_WEB_PUBLISHED
        ),
        FieldMapper('barcode', 'cplz05'),
        FieldMapper('tracking', 'gescsa', mapping=mappings.PRODUCT_TRACKING),
        FieldMapper(
            'taxes_id/id', 'gesctv',
            mapping=mappings.PRODUCT_SALE_VAT
        ),
        FieldMapper(
            'supplier_taxes_id/id', 'gesctv',
            mapping=mappings.PRODUCT_PURCHASE_VAT
        ),
        FieldMapper(
            'categ_id/id', 'gescsg',
            mapping=mappings.PRODUCT_CATEGORY
        ),
        FieldMapper(
            'state_id/id', 'geschr',
            mapping=mappings.PRODUCT_STATES
        ),
        FieldMapper(
            'unit_in_shrink_wrap', 'cp2z02',
        ),
        FieldMapper(
            'unit_in_box', 'cp2z04',
        ),
        FieldMapper(
            'unit_in_pallet', 'cp2z06',
        ),
        FieldMapper(
            'storage_temperature_id/id', 'cp2z17',
            mapping=mappings.PRODUCT_STORAGE_TEMPERATURES,
        ),
        FieldMapper(
            'ratio_main_product', 'cp2z23',
        ),
        FieldMapper(
            'ratio_additional_product', 'cp2z24',
        ),
        FieldMapper(
            'orderpoint_min', 'stomin'
        ),
        FieldMapper(
            'orderpoint_max', 'stomax'
        ),
        FieldMapper('route_ids/id', 'gescde', mapping=mappings.PRODUCT_ROUTES),
        'name', 'price_category_id', 'pb2', 'manufacturer',
        'orderpoint_qty_multiple'
    ]

    def get_sql_joins(self):
        return ("join sbdata.cplges on gesart=cplart"
                " left join sbdata.cplge2 on gesart=cp2art"
                " LEFT JOIN sbdata.PSTOCK ON (storef = GESART AND stosuc = 1)")

    def get_sql_where(self):
        if not self.importer.full:
            # TODO: csv only when mode will be developed
            return ("gesart IN ("
                    "    SELECT dccart FROM sbdata.PDETCDCL"
                    "        WHERE dccsui >= %s AND dccsui <= %s"
                    ")" % (SO_MIN, SO_MAX))
        return None

    def convert_name(self, odoo_entity, db2_entity):
        """ Dans la base DB2, si le nom commence par |||, || ou |,
        celà signifie que le produit est inactif.
        """
        value = db2_entity['gesdem'].strip()
        if value and value.startswith('|'):
            value = value.replace('|', '').strip()
            odoo_entity['active'] = False

        else:
            odoo_entity['active'] = True

        odoo_entity['name'] = value

    def convert_orderpoint_qty_multiple(self, odoo_entity, db2_entity):
        """
        Set the oderpoint qty multiple only if there is a stock max
        :param odoo_entity:
        :param db2_entity:
        :return:
        """
        if db2_entity['stomax']:
            odoo_entity['orderpoint_qty_multiple'] = \
                db2_entity['cp2z02'] or 1
        else:
            odoo_entity['orderpoint_qty_multiple'] = 0

    def convert_price_category_id(self, odoo_entity, db2_entity):
        value = db2_entity['gescre'].strip()
        if value:
            value = self.get_xml_id(
                'product_price_category', value.lower(),
                prefix='specific_product'
            )
        odoo_entity['price_category_id'] = OrderedDict(id=value)

    def _pricelist_item_product_price(
            self, pricelist_id, product_code, price, price_name
    ):
        self.importer.add_entity('pricelist_items', {
            'id': self.get_xml_id(
                'pricelist_item', 'product_%s_%s' % (product_code, price_name)
            ),
            'pricelist_id/id': pricelist_id,
            'applied_on': '1_product',
            'product_tmpl_id/id': self.get_xml_id(
                'product',
                '%s_product_template' % product_code
            ),
            'compute_price': 'fixed',
            'fixed_price': price,
        })

    def convert_pb2(self, odoo_entity, db2_entity):
        price1 = db2_entity.get('gespvr')
        price2 = db2_entity.get('gespv2')
        if price2 and price2 != price1:
            self._pricelist_item_product_price(
                'specific_data.product_pricelist_pb2',
                odoo_entity['default_code'],
                price2,
                'pb2'
            )

    MISSING_MANUFACTURERS = [
        '6452',
        '7411',
        '77319',
        '77411',
        '7953',
        '94502',
        '95550',
        '744115150',
    ]

    def convert_manufacturer(self, odoo_entity, db2_entity):
        """ Take manufacturer from imported suppliers """
        supplier_ref = db2_entity.get('cplz25')
        if supplier_ref:
            supplier_ref = str(int(supplier_ref))
            if supplier_ref in self.MISSING_MANUFACTURERS:
                print('skip manufacturer ref %s' % db2_entity.get('cplz25'))
                return

            self.importer.add_foreign_ref('FOURN', supplier_ref)
            supplier_xml_id = self.get_xml_id(
                'supplier', supplier_ref, '__import__')
            odoo_entity['manufacturer/id'] = supplier_xml_id


class AdditionalProductMapper(EntityMapper):
    # Create a second file to set additional_product_id
    # in order to have the product already existing
    DB2_NAME = 'PGESTION'

    XMLID_FIELD = 'id'
    # don't use additional_product
    XMLID_MODEL = 'product'

    FIELDS_MAPPING = [
        'id',
        'additional_product_id',
    ]

    def get_sql_joins(self):
        return (" left join sbdata.cplge2 on gesart=cp2art")

    def get_sql_where(self):
        where = "cp2z22 <> ''"
        if not self.importer.full:
            # TODO: csv only when mode will be developed
            where += (" AND gesart IN ("
                      "    SELECT dccart FROM sbdata.PDETCDCL"
                      "        WHERE dccsui >= %s AND dccsui <= %s"
                      ")"
                      " AND cp2z22 IN ("
                      "    SELECT dccart FROM sbdata.PDETCDCL"
                      "        WHERE dccsui >= %s AND dccsui <= %s"
                      ")" % (SO_MIN, SO_MAX, SO_MIN, SO_MAX))
        return where

    def convert_id(self, odoo_entity, db2_entity):
        """ Get product xmlid
        """
        odoo_entity['id'] = db2_entity['gesart']

    def convert_additional_product_id(self, odoo_entity, db2_entity):
        product = (db2_entity['cp2z22'] or '').strip()
        xmlid = self.get_xml_id('product', product, '__import__')
        odoo_entity['additional_product_id/id'] = xmlid


class Supplierinfo(EntityMapper):
    """ supplier info and promotions """
    DB2_NAME = 'PGESTION'

    XMLID_FIELD = 'id'

    # Doing a grouping to remove client column that creates duplicates
    GROUP_BY_COL = [
        'gesfou', 'gesart', 'gesarc', 'gespan', 'cclrem', 'cclref',
        'cclqu1', 'cclgr1',
        'ccldss', 'ccldaa', 'ccldmm', 'ccldjj',
        'cclfss', 'cclfaa', 'cclfmm', 'cclfjj']

    FIELDS_MAPPING = [
        'id',
        'name',
        FieldMapper('product_code', 'gesarc'),
        FieldMapper('price', 'gespan'),
        FieldMapper('discount_sale', 'cclrem'),
        FieldMapper('min_qty_sale', constant=1),
        FieldMapper('date_start', 'ccld', is_date=True),
        FieldMapper('date_end', 'cclf', is_date=True),
        'ratio_main_product',
        'ratio_promotional_product',
        'product_tmpl_id',
    ]

    def get_sql_select(self):
        return ','.join(self.GROUP_BY_COL)

    def get_sql_joins(self):
        """ Filter old promotions on the join and not promo from table condcf

        This way we either get one or more supplier info with promotion
        or we get a single supplier info without promotion

        """
        join = ("left join sbdata.condcf ON gesart=cclref"
                " AND cclpro = 1")
        if not self.importer.full:
            join += (" AND cclfss = 20 AND cclfaa >= 17"
                     " AND cclfmm >= 3 AND cclfmm <= 5")
        else:
            join += " AND cclfss = 20 AND cclfaa >= 16"
        return join

    def get_sql_where(self):
        # get only 2 years of promotions
        where = "gesfou IS NOT NULL"
        if not self.importer.full:
            # TODO: csv only when mode will be developed
            where += (
                      " AND gesart IN ("
                      "    SELECT dccart FROM sbdata.PDETCDCL"
                      "        WHERE dccsui >= %s AND dccsui <= %s"
                      ")" % (SO_MIN, SO_MAX))
        return where

    def get_group_by(self):
        """ We want to get rid of promotion per client, only one promotion
        is valid

        """
        return ','.join(self.GROUP_BY_COL)

    def convert_id(self, odoo_entity, db2_entity):
        """ Create a name from Supplier No + Product No + date
        """
        supplier = db2_entity['gesfou']
        product = db2_entity['gesart'].strip()
        ref = '%s-%s' % (supplier, product)
        if db2_entity['cclref']:
            year = db2_entity['ccldss'] * 100 + db2_entity['ccldaa']
            month = db2_entity['ccldmm']
            day = db2_entity['ccldjj']
            ref += '-%s%02i%02i' % (year, month, day)

        odoo_entity['id'] = ref

    def convert_name(self, odoo_entity, db2_entity):
        ref = db2_entity['gesfou']
        self.importer.add_foreign_ref('FOURN', ref)
        supplier_xml_id = self.get_xml_id(
            'supplier', str(ref), '__import__')
        odoo_entity['name/id'] = supplier_xml_id

    def convert_ratio_main_product(self, odoo_entity, db2_entity):
        qty = db2_entity['cclqu1'] or 0
        odoo_entity['ratio_main_product'] = int(qty)

    def convert_ratio_promotional_product(self, odoo_entity, db2_entity):
        qty = db2_entity['cclgr1'] or 0
        odoo_entity['ratio_promotional_product'] = int(qty)

    def convert_product_tmpl_id(self, odoo_entity, db2_entity):
        product = (db2_entity['gesart'] or '').strip()
        xmlid = self.get_xml_id('product', '%s_product_template' % product)
        odoo_entity['product_tmpl_id/id'] = xmlid


class CustomerMapper(EntityMapper):
    DB2_NAME = 'CLIENT'
    DB2_SCHEMA = 'gendata'

    XMLID_FIELD = 'ref'

    FIELDS_MAPPING = [
        FieldMapper('active', 'cliblf', mapping=mappings.CUSTOMER_ACTIVE),
        FieldMapper('ref', 'clinum'),
        FieldMapper('suite', 'clinos'),
        FieldMapper('name', 'clinom'),
        FieldMapper('street', 'cliadr'),
        FieldMapper('zip', 'clicpo'),
        FieldMapper('city', 'cliloc'),
        FieldMapper('fax', 'clifax'),
        FieldMapper('email', 'emwadr'),
        FieldMapper('vat', 'clicee', check=checks.vat),
        FieldMapper('vet_depot_number', 'clirch'),
        FieldMapper('vet_subscription_number', 'clirea'),
        FieldMapper(
            'alcyon_category_id/id', 'clista',
            mapping=mappings.PARTNER_ALCYON_CATEGORY,
        ),
        FieldMapper('country_id/id', 'clicpa',
                    mapping=mappings.COUNTRY),
        FieldMapper('title/id', 'clitit',
                    mapping=mappings.PARTNER_TITLE),
        FieldMapper('legal_entity', 'clitit',
                    mapping=mappings.PARTNER_LEGAL_ENTITY),
        FieldMapper(
            'discount_pricelist_id/id', 'clitrm',
            mapping=mappings.CLIENT_DISCOUNT_PRICELIST
        ),
        FieldMapper(
            'property_delivery_carrier_id/id', 'cliclv',
            mapping=mappings.CLIENT_DELIVERY_METHODS
        ),
        FieldMapper(
            'supplier_promotion_sale_allowed', 'clitrm',
            mapping=mappings.CLIENT_PROMOTION_PRICELIST
        ),
        FieldMapper(
            'user_id/id', 'clirep',
            mapping=mappings.USERS
        ),
        FieldMapper(
            'lang', 'clilan',
            mapping=mappings.LANG
        ),

        FieldMapper(
            'is_sale_back_order_accepted', 'clibor',
            mapping=mappings.BACKORDER_ACCEPTED
        ),

        FieldMapper(
            'property_payment_term_id/id',
            'clidel',
            mapping=mappings.CLIENT_PAYMENT_TERMS,
        ),
        FieldMapper(
            'customer_payment_mode_id/id',
            'clidel',
            mapping=mappings.CLIENT_PAYMENT_MODES,
            default=None
        ),
        FieldMapper(
            'is_price_on_labels',
            'cpcl05',
            mapping=mappings.STR_BOOL
        ),
        FieldMapper(
            'is_passport_required',
            'cpcl07',
            mapping=mappings.STR_BOOL
        ),

        'company_type', 'phone_numbers', 'product_pricelist',
        'customer_categories', 'pharmacist',
        'property_account_position_id',
        'comment',
    ]

    def get_sql_joins(self):
        return (
            "left join gendata.cplcli on clinum=cpcnum "
            # Email table (inspired by smile query, cf google drive)
            " left join gendata.emaweb "
            " on clinum=emwnum and emwcod=0 and emwcon=0 and emwtyp='E'"
            " and emwnli = (select min(emwnli) from gendata.emaweb"
            "   where clinum=emwnum and emwcod=0 and emwcon=0 and emwtyp='E'"
            " )"
        )

    def get_sql_where(self):
        if self.importer.full:
            return None
        # Filter sample of customer by customers on subset of sale orders
        # plus keep customers for delivery round
        return (
            "clinum"
            "  IN(SELECT ecccli FROM sbdata.PENTCDCL"
            "     WHERE eccsui >= %s AND eccsui <= %s)"
            " OR clinum in (1076, 1424, 148, 1658, 2112, 2139, 2141, 2151,"
            "               2157, 2169, 2171, 25, 280, 3201, 3375, 351, 3753,"
            "               3850, 4028, 4062, 4463, 4778, 5095, 5173, 5237,"
            "               5340, 5465, 5488, 5543, 5780, 7127, 7262, 7325,"
            "               7478, 7484, 8099, 8114, 8264, 8522, 8859,"
            "               91)" % (SO_MIN, SO_MAX)
            )

    @staticmethod
    def convert_company_type(odoo_entity, db2_entity):
        db2_title = db2_entity.get('clitit')

        if db2_title and db2_title not in mappings.PARTNER_TITLE:
            odoo_entity['company_type'] = 'company'
        else:
            odoo_entity['company_type'] = 'person'

    @staticmethod
    def convert_phone_numbers(odoo_entity, db2_entity):
        odoo_entity['phone'], odoo_entity['mobile'] = mappings.phone_converter(
            db2_entity.get('clitel'), db2_entity.get('clitlx')
        )

    @staticmethod
    def convert_product_pricelist(odoo_entity, db2_entity):
        code_remise = db2_entity.get('clista')
        if code_remise:
            if code_remise < 50:
                pricelist = 'specific_data.product_pricelist_pb1'
            else:
                pricelist = 'specific_data.product_pricelist_pb2'
        else:
            pricelist = None

        odoo_entity['property_product_pricelist/id'] = pricelist

    @staticmethod
    def convert_customer_categories(odoo_entity, db2_entity):
        odoo_entity['category_id/id'] = ",".join([
            mappings.CUSTOMER_CATEGORY[field_name]
            for field_name in mappings.CUSTOMER_CATEGORY.keys()
            if db2_entity[field_name] == 'Y'
        ]) or None

    def convert_pharmacist(self, odoo_entity, db2_entity):
        db2_id = db2_entity.get('cpcpha')

        if db2_id:
            self.importer.add_foreign_ref('FOURN', db2_id)
            xml_id = self.get_xml_id('supplier', db2_id, prefix='__import__')
        else:
            xml_id = None

        odoo_entity['pharmacist_id/id'] = xml_id

    @staticmethod
    def convert_property_account_position_id(odoo_entity, db2_entity):
        db2_vat_code = db2_entity.get('clictv')

        if db2_vat_code == 3:
            db2_country = db2_entity.get('clicpa')
            # See mappings.CEE_COUNTRIES
            if db2_country <= 12:
                code = 'intra'
            else:
                code = 'extra'
            pos = '__setup__.fiscal_position_' + code
        else:
            pos = mappings.CLIENT_FISCAL_POSITION[db2_vat_code]
        odoo_entity['property_account_position_id/id'] = pos

    @staticmethod
    def convert_comment(odoo_entity, db2_entity):
        # 4 lines of delivery notes
        lines = [
            db2_entity['cpcl29'], db2_entity['cpcl30'],
            db2_entity['cpcl31'], db2_entity['cpcl32']
        ]
        odoo_entity['comment'] = '\n'.join([l.strip() for l in lines if l])


class AddressMapper(EntityMapper):
    DB2_NAME = 'ADRLIV'
    DB2_REF_NAME = 'adlnum'

    XMLID_FIELD = 'ref'
    FIELDS_MAPPING = [
        FieldMapper('name', 'adlnom'),
        FieldMapper('street', 'adladr'),
        FieldMapper('zip', 'adlcpo'),
        FieldMapper('city', 'adlloc'),
        FieldMapper('phone', 'adltel'),
        FieldMapper('fax', 'adlfax'),
        FieldMapper('customer', constant=False),
        FieldMapper('supplier', constant=False),
        FieldMapper('country_id/id', 'adlcpa',
                    mapping=mappings.COUNTRY),
        FieldMapper('lang', 'adllan',
                    mapping=mappings.LANG),
        'phone_numbers',
        'type', 'ref', 'parent_id',
    ]

    @staticmethod
    def convert_phone_numbers(odoo_entity, db2_entity):
        odoo_entity['phone'], odoo_entity['mobile'] = mappings.phone_converter(
            db2_entity.get('adltel'), db2_entity.get('adltlx')
        )

    @staticmethod
    def convert_ref(odoo_entity, db2_entity):
        ttype = odoo_entity['type']
        parent = db2_entity['adlnum'].lstrip('0')
        odoo_entity['ref'] = "%s_%s" % (ttype, parent)

    @staticmethod
    def convert_type(odoo_entity, db2_entity):
        db2_type = db2_entity.get('adltyp')
        odoo_entity['type'] = 'delivery' if db2_type == 0 else 'invoice'

    @staticmethod
    def convert_parent_id(odoo_entity, db2_entity):
        db2_partner_type = db2_entity.get('adlcod')
        ref = db2_entity.get('adlnum').lstrip('0')

        if db2_partner_type == 1:
            partner_type = 'customer'
        elif db2_partner_type == 2:
            partner_type = 'supplier'
        # TODO type 3 == customer order addresses
        # todo with for the last 300 sale order only
        parent_xmlid = '__import__.%s_%s' % (partner_type, ref)
        odoo_entity['parent_id/id'] = parent_xmlid


class CustomerAddressMapper(AddressMapper):

    def get_sql_where(self):
        # Filter remove order delivery and invoicing adresses
        where = "adlcod = 1"
        if not self.importer.full:
            where += (
                # Filter num with wrong format with spaces in it
                # such as "1   2000"
                " AND NOT adlnum LIKE '%% %%' "
                "AND CAST(adlnum AS decimal)"
                "  IN(SELECT ecccli FROM sbdata.PENTCDCL"
                "     WHERE eccsui >= %s AND eccsui <= %s)" % (SO_MIN, SO_MAX)
            )
        return where


class SupplierMapper(EntityMapper):
    DB2_NAME = 'FOURN'
    DB2_REF_NAME = 'founum'

    XMLID_FIELD = 'ref'

    FIELDS_MAPPING = [
        FieldMapper('ref', 'founum'),
        FieldMapper('name', 'founom'),
        FieldMapper('street', 'fouadr'),
        FieldMapper('zip', 'foucpo'),
        FieldMapper('city', 'fouloc'),
        FieldMapper('phone', 'foutel'),
        FieldMapper('fax', 'foufax'),
        FieldMapper('email', 'emwadr'),
        FieldMapper('vat', 'foucee', check=checks.vat),
        FieldMapper('delivery_lead_time', 'foudll'),
        FieldMapper('customer', constant=False),
        FieldMapper('supplier', constant=True),
        FieldMapper('alcyon_category_id/id',
                    constant='specific_partner.partner_category_supplier'),
        FieldMapper('country_id/id', 'foucpa',
                    mapping=mappings.COUNTRY),
        FieldMapper('lang', 'foulan',
                    mapping=mappings.LANG),
        FieldMapper('is_purchase_back_order_accepted', constant=True),
        'phone_numbers',
    ]

    def get_sql_joins(self):
        return (
            # Email table (inspired by smile query, cf google drive)
            "left join gendata.emaweb "
            "on founum=emwnum and emwcod=1 and emwcon=0 and emwtyp='E' "
            "and emwnli = (select min(emwnli) from gendata.emaweb "
            "where founum=emwnum and emwcod=1 and emwcon=0 and emwtyp='E'"
            ")"
        )

    @staticmethod
    def convert_phone_numbers(odoo_entity, db2_entity):
        odoo_entity['phone'], odoo_entity['mobile'] = mappings.phone_converter(
            db2_entity.get('foutel'), db2_entity.get('foutlx')
        )


class LocationMapper(EntityMapper):
    DB2_NAME = 'PSTOCK'

    XMLID_FIELD = 'computed'

    FIELDS_MAPPING = [
        'name',
        'parent_id',
        'kind',
    ]

    def get_sql_query(self):
        """
        Some location don't have a control code.
        We don't need the secondary location (stolos)
        :return:
        """
        query = """
        SELECT storef, stolop FROM sbdata.PSTOCK
        WHERE CHAR_LENGTH(REPLACE(stolop, ' ', '')) >= 6
        AND SUBSTRING(stolop, 1, 1) IN ('A', 'E', 'G', 'P', 'Q')
        """
        if not self.importer.full:
            query += """
            AND storef IN (SELECT dccart
                        FROM sbdata.PDETCDCL
                        WHERE dccsui >= %s AND dccsui <= %s)
            """ % (SO_MIN, SO_MAX)

        return query, []

    def convert_entities(self, db2_entities):
        """ Create hierarchy first """
        odoo_entities = []

        locations = {}

        for db2_entity in db2_entities:
            value = db2_entity['stolop'].strip()
            if len(value) < 6:
                continue

            family = value[0]
            family_xmlid = self.get_xml_id(
                self.name, 'family_' + family
            )
            avenue = value[1]

            # If the third and fourth characters is a number, it means
            # that it is a standard location (eg: GC28C3).
            # Otherwise, it's a dynamic location (eg: GAE200).
            rack = value[2:4]
            if re.match(r'[0-9]{2}', rack):
                # Standard rack
                lvl = value[4]
                bin = value[5]
            else:
                # dynamic racks
                rack = value[2]
                lvl = value[3]
                bin = value[4:6]

            control_code = value[6:8]

            bin_xmlid = self.get_xml_id(
                self.name, 'loc_' + family + avenue + rack + lvl + bin)

            # remove duplicates
            if bin_xmlid in locations:
                # try to find as many control code as possible
                if control_code and not locations[bin_xmlid]['bin_checksum_1']:
                    locations[bin_xmlid]['bin_checksum_1'] = control_code
                continue

            odoo_entity = OrderedDict(id=None)
            odoo_entity['name'] = family + avenue + rack + lvl + bin
            odoo_entity['bin_checksum_1'] = control_code
            odoo_entity['location_id/id'] = family_xmlid
            odoo_entity['id'] = bin_xmlid
            odoo_entity['kind'] = 'bin'
            odoo_entity['zone'] = family
            odoo_entity['corridor'] = avenue
            odoo_entity['shelf'] = rack
            odoo_entity['height'] = lvl
            odoo_entity['box'] = bin
            odoo_entities.append(odoo_entity)

            locations[bin_xmlid] = odoo_entity

        return odoo_entities


class SaleOrderMapper(EntityMapper):
    DB2_NAME = 'PENTCDCL'
    DB2_SCHEMA = 'sbdata'

    XMLID_FIELD = 'id'

    FIELDS_MAPPING = [
        FieldMapper('name', 'eccsui'),
        FieldMapper('origin', 'eccrin'),
        FieldMapper('client_order_ref', 'eccrcl'),
        FieldMapper(
            'user_id/id', 'eccrep',
            mapping=mappings.USERS
        ),
        FieldMapper('state', constant='draft'),
        # BEF is used in old commands we won't import
        FieldMapper('currency_id/id', constant="base.EUR"),
        FieldMapper('date_order', 'eccd', is_date=True),
        'id', 'partner_id',
    ]

    def convert_id(self, odoo_entity, db2_entity):
        """ Create a name from Suite No + Client No + User No
        We use user to remove duplicates """
        suite = db2_entity['eccsui']
        client = db2_entity['ecccli']
        store = db2_entity['eccsuc'].strip()
        odoo_entity['id'] = "%s_%s_%s" % (suite, client, store)

    def convert_partner_id(self, odoo_entity, db2_entity):
        ref = db2_entity['ecccli']
        xmlid = '__import__.%s_%s' % ('customer', ref)
        odoo_entity['partner_id/id'] = xmlid

    def get_sql_where(self):
        where = "eccncr = 0 AND "
        if not self.importer.full:
            where = "eccsui >= %s AND eccsui <= %s" % (SO_MIN, SO_MAX)
        else:
            where = ("ecccss = 20 AND ecccaa = 17 AND ecccmm = 5")
        return where

    def get_order_by(self):
        return "eccsui"

    def get_xml_id(self, entity_name, code, prefix=None):
        """ Force use of sale_order to avoid having
        sale_order_closed and sale_order_open in xml ids """
        assert entity_name and code

        entity_name = "sale_order"

        if prefix is None:
            prefix = self.XMLID_IMPORT_NAME

        return "%s.%s_%s" % (
            prefix, entity_name, code
        )


class SaleOrderLineMapper(EntityMapper):
    DB2_NAME = 'PDETCDCL'
    DB2_SCHEMA = 'sbdata'

    XMLID_FIELD = 'id'

    FIELDS_MAPPING = [
        FieldMapper('sequence', 'dccnli'),
        FieldMapper('name', 'dcclib'),
        FieldMapper('product_uom_qty', 'dccquc'),
        FieldMapper('product_uom/id', constant='product.product_uom_unit'),
        FieldMapper('qty_delivered', 'dccqul'),
        FieldMapper('price_unit', 'dccpvd'),
        FieldMapper('discount', 'dccrem'),
        'id', 'product_id', 'order_id'
        # TODO taxes ?
    ]

    def convert_id(self, odoo_entity, db2_entity):
        """ Create a name from Suite No + Client No + User No + Line numeber
        We use user to remove duplicates
        """
        suite = db2_entity['dccsui']
        client = db2_entity['dccncl']
        store = db2_entity['dccsuc'].strip()
        line_num = db2_entity['dccnli']
        odoo_entity['id'] = "%s_%s_%s_%s" % (suite, client, store, line_num)

    def convert_product_id(self, odoo_entity, db2_entity):

        product = (db2_entity['dccart'] or '').strip()
        if product:
            xmlid = self.get_xml_id('product', product, '__import__')
        else:
            xmlid = '__setup__.product_other'
            odoo_entity['name'] = "Divers"
        odoo_entity['product_id/id'] = xmlid

    def convert_order_id(self, odoo_entity, db2_entity):
        suite = db2_entity['eccsui']
        client = db2_entity['ecccli']
        store = db2_entity['eccsuc'].strip()
        code = "%s_%s_%s" % (suite, client, store)
        xmlid = self.get_xml_id('sale_order', code, '__import__')
        odoo_entity['order_id/id'] = xmlid

    def get_sql_joins(self):
        return ("join sbdata.PENTCDCL ON"
                "    eccsui=dccsui"
                "    AND ecccli=dccncl"
                "    AND eccsuc=dccsuc ")

    def get_sql_where(self):
        where = None
        if not self.importer.full:
            where = "dccsui >= %s AND dccsui <= %s" % (SO_MIN, SO_MAX)
        else:
            where = "dcccss = 20 AND dcccaa = 17"
        return where

    def get_order_by(self):
        return "eccsui, ecccli, eccsuc"


class StockProductionLotMapper(EntityMapper):
    DB2_NAME = 'PLOTS'

    XMLID_FIELD = "id"

    FIELDS_MAPPING = {
        'id': concat('lotnum', 'lotref', delimiter='_'),
        'name': 'lotnum',
        'product_id/id': ref('product', 'lotref', '__import__', check=False),
        'checksum':
            lambda rec: rec['vloint'] and
            ('000'+'{:.0f}'.format(rec['vloint']))[-3:] or '',
        'life_date': lambda rec:
            rec['vloech'] and
            int('{:.0f}'.format(rec['vloech'])) != 99999999 and
            datetime.strptime('{:.0f}'.format(rec['vloech']), '%Y%m%d')
                    .strftime('%Y-%m-%d 00:00:00') or '2000-01-01 00:00:00',
    }
    def get_sql_select(self):
        return "lotref,lotnum,v.vloint,v.vloech"

    def get_sql_joins(self):
        return ("""
            LEFT JOIN sbdata.vplots v ON (lotref=v.vloart AND lotnum=v.vlolot)
            LEFT OUTER JOIN sbdata.vplots v2 ON
                (v.vloart=v2.vloart AND v.vlolot=v2.vlolot
                AND v2.vloech>v.vloech)
        """)

    def get_sql_where(self):
        # Warning: some lot are existing multiple times.
        # Could be that the supplier re-emitted the lot with another life date,
        # or there was encoding error at reception
        # res=fetchall_dict("""
        #   SELECT lotnum,lotref,lotdes||lotdea,count(vloech) FROM sbdata.PLOTS
        #   LEFT JOIN sbdata.vplots ON lotnum=vlolot AND lotref=vloart
        #   WHERE lotact !=0 group by lotnum, lotref,lotdes||lotdea
        #   having count(vloech)>1  ORDER BY 1 asc""")
        # We cannot use the date as key in the join between plots and vplots as
        # 28% of dates cannot be matched and there is nothing to get last
        # inserted/modified record.
        # So, I apply the greatest-n-per-group on vplots to fetch the date and
        # checksum.

        where = """
        lotact !=0
        AND lotsuc='1'
        AND v2.vloech is null
        """
        if not self.importer.full:
            where += """
            AND lotref IN (SELECT dccart
            FROM sbdata.PDETCDCL
            WHERE dccsui >= %s AND dccsui <= %s)
            """ % (SO_MIN, SO_MAX)
        return where


class StockInventoryLineMapper(EntityMapper):
    DB2_NAME = 'PLOTS'

    XMLID_FIELD = "id"

    FIELDS_MAPPING = {
        'id': concat('lotnum', 'lotref', delimiter='_'),
        'prod_lot_id/id':
            ref('stock_production_lot',
                concat('lotnum', 'lotref', delimiter='_'),
                '__import__', check=False),
        'product_id/id': ref('product', 'lotref', '__import__', check=False),
        'product_qty': lambda rec: max(int(rec['lotact']), 0),
        'location_id/id': ref('location',
                              concat(const('loc'),
                                     call(lambda rec: rec['stolop'][:6]),
                                     delimiter='_'),
                              '__import__', check=False),
    }

    def get_sql_joins(self):
        return ("""
            LEFT JOIN sbdata.vplots v ON (lotref=v.vloart AND lotnum=v.vlolot)
            LEFT JOIN sbdata.pstock ON (storef=lotref AND stosuc=lotsuc)
            LEFT JOIN sbdata.pgestion ON gesart=lotref
        """)

    def get_sql_where(self):
        where = """
            lotact !=0
            AND lotsuc='1'
            AND CHAR_LENGTH(REPLACE(stolop, ' ', '')) >= 6
            AND SUBSTRING(stolop, 1, 1) IN ('A', 'E', 'G', 'P', 'Q')
        """
        if not self.importer.full:
            where += """
            AND lotref IN (SELECT dccart
                                    FROM sbdata.PDETCDCL
                                    WHERE dccsui >= %s AND dccsui <= %s)
            """ % (SO_MIN, SO_MAX)
        return where


class ProductStockBinMapper(EntityMapper):
    DB2_NAME = 'PSTOCK'

    XMLID_FIELD = "id"

    FIELDS_MAPPING = {
        'id': concat('storef', 'location_name', delimiter='_'),
        'product_id/id': lambda rec:
            ref('product', 'storef', '__import__', check=False)(rec) +
            '_product_template',
        'location_id/id': const('stock.stock_location_stock'),
        'bin_location_id/id': ref('location',
                                  concat(const('loc'),
                                         call(lambda rec: rec['stolop'][:6]),
                                         delimiter='_'),
                                  '__import__', check=False),
    }

    def get_sql_query(self):
        query = """
        SELECT storef, stolop FROM sbdata.PSTOCK
        WHERE CHAR_LENGTH(REPLACE(stolop, ' ', '')) >= 6
        AND SUBSTRING(stolop, 1, 1) IN ('A', 'E', 'G', 'P', 'Q')
        """
        if not self.importer.full:
            query += """
                    AND storef IN (SELECT dccart
                                FROM sbdata.PDETCDCL
                                WHERE dccsui >= %s AND dccsui <= %s)
                    """ % (SO_MIN, SO_MAX)
        return query, []


class StockInventoryLineWithoutLot(EntityMapper):
    DB2_NAME = 'PSTOCK'

    XMLID_FIELD = "id"

    PRODUCT_WITHOUT_LOT_KEY = [key for key, value
                               in mappings.PRODUCT_TRACKING.iteritems()
                               if value == 'none']

    FIELDS_MAPPING = {
        'id': concat('storef', delimiter='_'),
        'product_id/id': ref('product', 'storef', '__import__', check=False),
        'product_qty': lambda rec: max(int(rec['stosto']), 0),
        'location_id/id': ref('location',
                              concat(const('loc'),
                                     call(lambda rec: rec['stolop'][:6]),
                                     delimiter='_'),
                              '__import__', check=False),
    }

    def get_sql_query(self):
        """
        Take only stock from depot 1 (PSTOCK.stosuc = 1)
        and products without lot (PGESTION.gesca = 0)
        :return:
        """
        query = """
        SELECT storef, stolop, stosto FROM sbdata.PSTOCK
          INNER JOIN SBDATA.PGESTION ON GESART = STOREF
        WHERE CHAR_LENGTH(REPLACE(stolop, ' ', '')) >= 6
        AND SUBSTRING(stolop, 1, 1) IN ('A', 'E', 'G', 'P', 'Q')
        AND stosuc = '1'
        AND gescsa = '0'
        """
        if not self.importer.full:
            query += """
                    AND storef IN (SELECT dccart
                                FROM sbdata.PDETCDCL
                                WHERE dccsui >= %s AND dccsui <= %s)
                    """ % (SO_MIN, SO_MAX)
        return query, []


class StockInventoryLineWithSerial(EntityMapper):
    DB2_NAME = 'PSTOCK'

    XMLID_FIELD = "id"

    PRODUCT_WITHOUT_LOT_KEY = [key for key, value
                               in mappings.PRODUCT_TRACKING.iteritems()
                               if value == 'none']

    FIELDS_MAPPING = {
        'id': concat('storef', delimiter='_'),
        'product_id/id': ref('product', 'storef', '__import__', check=False),
        'product_qty': lambda rec: max(int(rec['stosto']), 0),
        'location_id/id': ref('location',
                              concat(const('loc'),
                                     call(lambda rec: rec['stolop'][:6]),
                                     delimiter='_'),
                              '__import__', check=False),
    }

    def get_sql_query(self):
        """
        Take only stock from depot 1 (PSTOCK.stosuc = 1)
        and products with serial number (PGESTION.gesca = 4)
        :return:
        """
        query = """
        SELECT storef, stolop, stosto FROM sbdata.PSTOCK
          INNER JOIN SBDATA.PGESTION ON GESART = STOREF
        WHERE CHAR_LENGTH(REPLACE(stolop, ' ', '')) >= 6
        AND SUBSTRING(stolop, 1, 1) IN ('A', 'E', 'G', 'P', 'Q')
        AND stosuc = '1'
        AND gescsa = '4'
        """
        if not self.importer.full:
            query += """
                    AND storef IN (SELECT dccart
                                FROM sbdata.PDETCDCL
                                WHERE dccsui >= %s AND dccsui <= %s)
                    """ % (SO_MIN, SO_MAX)
        return query, []


class ProductNewRouteInfo(EntityMapper):
    """Get data for locator with 1 letter A, E, G, P and Q

    Write field description_picking on product to assign
    routes on post-process."""
    DB2_NAME = 'PSTOCK'

    XMLID_FIELD = "id"
    XMLID_MODEL = 'product'

    FIELDS_MAPPING = [
        'id',
        FieldMapper('description_picking', 'stolop'),
    ]

    def get_sql_query(self):
        query = """
        SELECT storef, stolop FROM sbdata.PSTOCK
        WHERE CHAR_LENGTH(REPLACE(stolop, ' ', '')) = 1
        AND SUBSTRING(stolop, 1, 1) IN ('A', 'E', 'G', 'P', 'Q')
        """
        if not self.importer.full:
            query += """
                    AND storef IN (SELECT dccart
                                FROM sbdata.PDETCDCL
                                WHERE dccsui >= %s AND dccsui <= %s)
                    """ % (SO_MIN, SO_MAX)
        return query, []

    def convert_id(self, odoo_entity, db2_entity):
        """ Get product xmlid
        """
        odoo_entity['id'] = db2_entity['storef']


MAPPER_CLASSES = [LocationMapper, ProductMapper,
                  AdditionalProductMapper,
                  Supplierinfo,
                  CustomerMapper, SupplierMapper,
                  CustomerAddressMapper,
                  SaleOrderMapper,
                  SaleOrderLineMapper,
                  StockProductionLotMapper,
                  StockInventoryLineMapper,
                  ProductStockBinMapper,
                  StockInventoryLineWithoutLot,
                  StockInventoryLineWithSerial,
                  ProductNewRouteInfo,
                  ]

MAPPER_CLASSES_FULL = [LocationMapper, ProductMapper,
                       AdditionalProductMapper,
                       Supplierinfo,
                       CustomerMapper, SupplierMapper,
                       CustomerAddressMapper,
                       StockProductionLotMapper,
                       StockInventoryLineMapper,
                       ProductStockBinMapper,
                       StockInventoryLineWithoutLot,
                       StockInventoryLineWithSerial,
                       ProductNewRouteInfo,
                       ]
