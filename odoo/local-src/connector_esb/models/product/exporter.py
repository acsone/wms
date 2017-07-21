# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import bool2int, dt2esbdate


class ProductExportMapper(Component):
    _name = 'esb.product.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.product'

    direct = [
        ('name', 'Gesdem'),
        ('default_code', 'Gesart'),
        ('barcode', 'Cplz05'),
        ('weight', 'Gespnt'),
        (bool2int('active'), 'Cplz19'),
        (dt2esbdate('create_date'), 'Gescrt'),
        ('volume', 'Cp2z08'),
        ('cnk_code', 'Cplz03'),
        ('depth', 'Cp2z01'),
        ('length', 'Cp2z03'),
        ('width', 'Cp2z05'),
    ]

    translatable_keys = {
        'nl_BE': {
            'name': 'Refdem',
        }
    }

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'product')

    @mapping
    def supplier(self, record):
        supplier_product_code = ''
        supplier_ref = ''
        suppliers = record.seller_ids
        if suppliers:
            supplier = suppliers[0]
            supplier_product_code = supplier.product_code
            supplier_ref = supplier.name.ref
        return {'Gesarc': supplier_product_code,
                'Gesfou': supplier_ref,
                # "fabricant" could maybe be removed
                'Cplz25': supplier_ref,
                }

    @mapping
    def fixed_fields(self, record):
        """ return hardcoded values for fields """
        empty = ('Cp2z22', 'Warceg', 'Warcfr', 'Warcnl')
        zero = ('Gescsg', 'Cp2z02', 'Cp2z23', 'Cp2z24', 'Cplz29',
                'Cp2z17', 'Cp2z19', 'LotEch')
        values = {f: '' for f in empty}
        values.update({f: 0 for f in zero})
        return values

    @mapping
    def taxes(self, record):
        ref = ''
        contrib_sku = ''
        for tax in record.taxes_id:
            if tax.esb_ref and not ref:
                ref = tax.esb_ref  # first found
            if tax.contrib_sku and not contrib_sku:
                contrib_sku = tax.contrib_sku  # first found
        return {'Gesctv': ref, 'Cplz07': contrib_sku}

    @mapping
    def lot_tracking(self, record):
        return {'Gescsa': 1 if record.tracking != 'none' else 0}

    @mapping
    def stockable(self, record):
        return {'Gescge': 1 if record.type == 'product' else 0}

    @mapping
    def splittable(self, record):
        # 1 when we sell units, 0 when we decimals of a unit are possible
        return {'Gescov': 0 if record.uom_id.rounding < 1.0 else 1}

    @mapping
    def price_categs(self, record):
        categs = ('GMA', 'ALI', 'ALG', 'ALH', 'IMP')
        values = dict.fromkeys(categs, 0)
        categ = record.price_category_id.name
        if categ:
            values[categ] = 1
        return values

    @mapping
    def uom(self, record):
        return {'Gesunv': record.uom_id.esb_ref or ''}

    @mapping
    def mto(self, record):
        warehouses = self.env['stock.warehouse'].search([])
        mto_routes = warehouses.mapped('mto_pull_id.route_id')
        routes = record.route_ids
        is_mto = 1 if set(routes.ids).intersection(mto_routes.ids) else 0
        return {'Gescde': is_mto}

    @mapping
    def todo(self, record):
        """ TODO: fields to map, hardcoded for now """
        return {
            'Cplz14': '',
        }


class ProductCronExporter(Component):

    _name = 'esb.product.cron.exporter'
    _inherit = ['esb.cron.exporter', ]
    _usage = 'record.exporter.cron'
    _apply_on = 'product.product'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'product')

    def get_items_domain(self):
        domain = [
            # GESCHR!=’L’ (non livrables)
            # TODO: which field/attribute/condition is this???
            # not GESTART.startwith(‘8888’) (contrib antibio)
            ('default_code', 'not like', '8888%'),
            # Articles créés depuis 29/7/2014
            ('create_date', '>', '2014-7-29 00:00:00'),
        ]
        return domain

    def _export_items(self, items):
        result = super(ProductCronExporter, self)._export_items(items)
        new_exported = self.model.search(
            [('id', 'in', items.ids), ('esb_exported', '=', False)],
        )
        # we flag the products as exported, bypassing the ORM
        # otherwise the write_date would be modified and the records
        # exported again...
        self.env.cr.execute(
            "UPDATE product_product SET esb_exported = true "
            "WHERE id IN %s ", (tuple(new_exported.ids),)
        )
        self.model.invalidate_cache(
            fnames=['esb_exported'],
            ids=new_exported.ids
        )
        return result
