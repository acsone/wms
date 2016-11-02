# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from collections import OrderedDict, defaultdict

from base import EntityMapper, FieldMapper
import checks
import mappings


class ProductMapper(EntityMapper):
    DB2_NAME = 'PGESTION'

    XMLID_FIELD = 'default_code'

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
        'name', 'price_category_id', 'seller_ids', 'pb2'
    ]

    def get_sql_joins(self):
        return "join sbdata.cplges on gesart=cplart "

    def get_sql_where(self):
        # TODO: csv only when mode will be developed
        return "gesdem not like '|||%'"

    def convert_name(self, odoo_entity, db2_entity):
        """ Dans la base DB2, si le nom commence par |||, celà signifie que le
        produit est inactif.
        """
        value = db2_entity['gesdem'].strip()
        if value and value.startswith('|||'):
            value = value.replace('||| ', '')
            odoo_entity['active'] = False

        else:
            odoo_entity['active'] = True

        odoo_entity['name'] = value

    def convert_price_category_id(self, odoo_entity, db2_entity):
        value = db2_entity['gescre'].strip()
        if value:
            value = self.get_xml_id(
                'product_price_category', value.lower()
            )
        odoo_entity['price_category_id'] = OrderedDict(id=value)

    def convert_seller_ids(self, odoo_entity, db2_entity):
        ref = db2_entity['gesfou']
        if ref:
            self.importer.add_foreign_ref('FOURN', ref)
            xml_id = self.get_xml_id(
                'supplierinfo', '%s-%s' % (ref, db2_entity['gesart'].strip())
            )
            supplier_xml_id = self.get_xml_id('supplier', str(ref))

            self.importer.add_entity('supplierinfo', {
                'id': xml_id,
                'name/id': supplier_xml_id,
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
                'scenario.product_pricelist_pb2',
                odoo_entity['default_code'],
                price2,
                'pb2'
            )


class CustomerMapper(EntityMapper):
    DB2_NAME = 'CLIENT'
    DB2_SCHEMA = 'gendata'

    XMLID_FIELD = 'ref'

    FIELDS_MAPPING = [
        FieldMapper('ref', 'clinum'),
        FieldMapper('name', 'clinom'),
        FieldMapper('street', 'cliadr'),
        FieldMapper('zip', 'clicpo'),
        FieldMapper('city', 'cliloc'),
        FieldMapper('fax', 'clifax'),
        FieldMapper('email', 'emwadr'),
        FieldMapper('depot_number', 'clirch'),
        FieldMapper(
            'alcyon_category_id/id', 'clista',
            mapping=mappings.PARTNER_CATEGORY,
        ),
        FieldMapper('country_id/id', 'clicpa',
                    mapping=mappings.COUNTRY),
        FieldMapper('title/id', 'clitit',
                    mapping=mappings.PARTNER_TITLE),
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

        'company_type', 'phone_numbers',
    ]

    def get_sql_joins(self):
        return (
            # Email table (inspired by smile query, cf google drive)
            "left join gendata.emaweb "
            "on clinum=emwnum and emwcod=0 and emwcon=0 and emwtyp='E' "
            "and emwnli = (select min(emwnli) from gendata.emaweb "
            "where clinum=emwnum and emwcod=0 and emwcon=0 and emwtyp='E'"
            ")"
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
        FieldMapper('country_id/id', 'foucpa',
                    mapping=mappings.COUNTRY),
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


MAPPER_CLASSES = [ProductMapper, CustomerMapper, SupplierMapper]
