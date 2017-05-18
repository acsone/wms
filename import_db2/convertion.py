# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import OrderedDict, defaultdict

from base import EntityMapper, FieldMapper
import checks
import mappings

# Sample data for 302 SO
SO_MIN = 2691474
SO_MAX = 2691777


class ProductMapper(EntityMapper):
    DB2_NAME = 'PGESTION'

    XMLID_FIELD = 'default_code'
    XMLID_IMPORT_NAME = '__import__'

    FIELDS_MAPPING = [
        FieldMapper('default_code', 'gesart'),
        FieldMapper('list_price', 'gespvr'),
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
        FieldMapper('route_ids/id', 'gescde', mapping=mappings.PRODUCT_ROUTES),
        'name', 'price_category_id', 'seller_ids', 'pb2'
    ]

    def get_sql_joins(self):
        return "join sbdata.cplges on gesart=cplart "

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

    def convert_price_category_id(self, odoo_entity, db2_entity):
        value = db2_entity['gescre'].strip()
        if value:
            value = self.get_xml_id(
                'product_price_category', value.lower(), prefix='__setup__'
            )
        odoo_entity['price_category_id'] = OrderedDict(id=value)

    def convert_seller_ids(self, odoo_entity, db2_entity):
        ref = db2_entity['gesfou']
        if ref:
            self.importer.add_foreign_ref('FOURN', ref)
            xml_id = self.get_xml_id(
                'supplierinfo', '%s-%s' % (ref, db2_entity['gesart'].strip())
            )
            supplier_xml_id = self.get_xml_id(
                'supplier', str(ref), '__import__')

            price = db2_entity['gespan']
            vendor_code = db2_entity['gesarc'].strip()

            self.importer.add_entity('supplierinfo', {
                'id': xml_id,
                'name/id': supplier_xml_id,
                'product_code': vendor_code,
                'price': price,
                'product_tmpl_id/id': self.get_xml_id(
                    'product',
                    '%s_product_template' % odoo_entity['default_code']
                )
            })

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
                '__setup__.product_pricelist_pb2',
                odoo_entity['default_code'],
                price2,
                'pb2'
            )


class CustomerMapper(EntityMapper):
    DB2_NAME = 'CLIENT'
    DB2_SCHEMA = 'gendata'

    XMLID_FIELD = 'ref'
    XMLID_IMPORT_NAME = '__import__'

    FIELDS_MAPPING = [
        FieldMapper('active', 'cliblf', mapping=mappings.CUSTOMER_ACTIVE),
        FieldMapper('ref', 'clinum'),
        FieldMapper('name', 'clinom'),
        FieldMapper('street', 'cliadr'),
        FieldMapper('zip', 'clicpo'),
        FieldMapper('city', 'cliloc'),
        FieldMapper('fax', 'clifax'),
        FieldMapper('email', 'emwadr'),
        FieldMapper('vat', 'clicee', check=checks.vat),
        FieldMapper('depot_number', 'clirch'),
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
            'promotion_pricelist_id/id', 'clitrm',
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

        'company_type', 'phone_numbers', 'product_pricelist',
        'customer_categories', 'pharmacist',
        'property_account_position_id',
    ]

    def get_sql_joins(self):
        return (
            "left join gendata.cplcli on clinum=cpcnum "
            # Email table (inspired by smile query, cf google drive)
            "left join gendata.emaweb "
            "on clinum=emwnum and emwcod=0 and emwcon=0 and emwtyp='E' "
            "and emwnli = (select min(emwnli) from gendata.emaweb "
            "where clinum=emwnum and emwcod=0 and emwcon=0 and emwtyp='E'"
            ")"
        )

    def get_sql_where(self):
        if self.importer.full:
            return None
        # Filter sample of customer by customers on last sale orders
        return (
            "clinum"
            "  IN(SELECT ecccli FROM sbdata.PENTCDCL"
            "     WHERE eccsui >= %s AND eccsui <= %s)" % (SO_MIN, SO_MAX)
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
                pricelist = '__setup__.product_pricelist_pb1'
            else:
                pricelist = '__setup__.product_pricelist_pb2'
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
        FieldMapper('customer', constant=False),
        FieldMapper('supplier', constant=True),
        FieldMapper('alcyon_category_id/id',
                    constant='__setup__.partner_category_supplier'),
        FieldMapper('country_id/id', 'foucpa',
                    mapping=mappings.COUNTRY),
        FieldMapper('lang', 'foulan',
                    mapping=mappings.LANG),
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
    XMLID_IMPORT_NAME = '__import__'

    FIELDS_MAPPING = [
        'name',
        'parent_id',
        'kind',
    ]

    def get_sql_query(self):
        query = ("select p1.stolos as location_name from sbdata.PSTOCK as p1"
                 " UNION "
                 "select p2.stolop as location_name from sbdata.PSTOCK as p2")
        if not self.importer.full:
            query += " FETCH FIRST 300 ROWS ONLY"

        return query, []

    def convert_entities(self, db2_entities):
        """ Create hierarchy first """
        odoo_entities = []

        locations = {}

        for db2_entity in db2_entities:
            value = db2_entity['location_name'].strip()
            if len(value) < 8:
                continue

            family = value[0]
            family_xmlid = self.get_xml_id(
                self.name, 'family_' + family
            )
            avenue = value[1]

            if family in ('A', 'P'):
                rack = value[2:4]
                lvl = value[4]
                bin = '0' + value[5]
            elif family in ('Q', 'E'):
                rack = value[2]
                lvl = value[3]
                bin = value[4:6]
            elif family == 'G':
                # dynamic racks
                rack = value[2]
                lvl = value[3]
                bin = value[4:6]
                # TODO not found in PSTOCK non dynamic racks
            else: # skip V, W and other unknown
                continue

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
    XMLID_IMPORT_NAME = '__import__'

    FIELDS_MAPPING = [
        FieldMapper('name', 'eccsui'),
        FieldMapper('origin', 'eccrin'),
        FieldMapper('client_order_ref', 'eccrcl'),
        FieldMapper(
            'user_id/id', 'eccrep',
            mapping=mappings.USERS
        ),
        # BEF is used in old commands we won't import
        FieldMapper('currency_id/id', constant="base.EUR"),
        'id', 'date_order', 'partner_id',
    ]

    def convert_id(self, odoo_entity, db2_entity):
        """ Create a name from Suite No + Client No + User No
        We use user to remove duplicates """
        suite = db2_entity['eccsui'] 
        client = db2_entity['ecccli']
        user = db2_entity['eccuti']
        odoo_entity['id'] = "%s_%s_%s" % (suite, client, user)

    def convert_date_order(self, odoo_entity, db2_entity):
        dd = db2_entity['eccdjj']
        mm = db2_entity['eccdmm']
        Y = "%s%s" % (db2_entity['eccdss'], db2_entity['eccdaa'])
        odoo_entity['date_order'] = "%s-%02i-%02i" % (Y, mm, dd)

    def convert_partner_id(self, odoo_entity, db2_entity):
        ref = db2_entity['ecccli']
        xmlid = '__import__.%s_%s' % ('customer', ref)
        odoo_entity['partner_id/id'] = xmlid

    def get_sql_where(self):
        where = None
        if not self.importer.full:
            where = "eccsui >= %s AND eccsui <= %s" % (SO_MIN, SO_MAX)
        else:
            where = "ecccss = 20 AND ecccaa = 17"
        return where

    def get_order_by(self):
        return "eccsui"


class SaleOrderLineMapper(EntityMapper):
    DB2_NAME = 'PDETCDCL'
    DB2_SCHEMA = 'sbdata'

    XMLID_FIELD = 'id'
    XMLID_IMPORT_NAME = '__import__'

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
        user = db2_entity['dccuti']
        line_num = db2_entity['dccnli']
        odoo_entity['id'] = "%s_%s_%s_%s" % (suite, client, user, line_num)

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
        user = db2_entity['eccuti']
        code = "%s_%s_%s" % (suite, client, user)
        xmlid = self.get_xml_id('sale_order', code, '__import__')
        odoo_entity['order_id/id'] = xmlid

    def get_sql_joins(self):
        return ("join sbdata.PENTCDCL ON"
                "    eccsui=dccsui"
                "    AND ecccli=dccncl"
                "    AND eccuti=dccuti ")

    def get_sql_where(self):
        where = None
        if not self.importer.full:
            where = "dccsui >= %s AND dccsui <= %s" % (SO_MIN, SO_MAX)
        else:
            where = "dcccss = 20 AND dcccaa = 17"
        return where

    def get_order_by(self):
        return "eccsui, ecccli, eccuti"


MAPPER_CLASSES = [LocationMapper, ProductMapper,
                  CustomerMapper, SupplierMapper,
                  CustomerAddressMapper,
                  SaleOrderMapper,
                  SaleOrderLineMapper]
