# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import bool2int, dt2esbdate, falsy2emptystring


class ProductExportMapper(Component):
    _name = 'esb.product.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.product'

    direct = [
        ('name', 'Gesdem'),
        (falsy2emptystring('default_code'), 'Gesart'),
        (falsy2emptystring('barcode'), 'Cplz05'),
        ('weight', 'Gespnt'),
        (bool2int('active'), 'Cplz19'),
        (dt2esbdate('create_date'), 'Gescrt'),
        ('volume', 'Cp2z08'),
        (falsy2emptystring('cnk_code'), 'Cplz03'),
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
            supplier_product_code = supplier.product_code or ''
            supplier_ref = supplier.name.ref or ''
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
        values = dict.fromkeys(categs, False)
        categ = record.price_category_id.name
        if categ:
            values[categ] = True
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

    _mark_as_exported = True

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

    def _write_esb_exported_mark_on_records(self, records):
        _super = super(ProductCronExporter, self)
        _super._write_esb_exported_mark_on_records(records)
        # product_template.esb_exported is a computed field based on
        # product_product.esb_exported, but as we bypass the ORM to
        # write in product_product, the computation won't be triggered
        # do the same here. (it bypasses the ORM to avoid to update the
        # write_date which would trigger a new update)
        templates = records.mapped('product_tmpl_id')
        query = (
            "UPDATE %s SET esb_exported = true "
            "WHERE id IN %%s " % (templates._table,)
        )
        self.env.cr.execute(query, (tuple(templates.ids),))
        self.model.invalidate_cache(
            fnames=['esb_exported'],
            ids=templates.ids
        )
