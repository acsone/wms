# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import bool2int, dt2esbdate, falsy2emptystring
from ...components.mapper import falsy2zero


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
        (falsy2zero('unit_in_shrink_wrap'), 'Cp2z02'),
        (falsy2zero('ratio_main_product'), 'Cp2z23'),
        (falsy2zero('ratio_additional_product'), 'Cp2z24'),
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
        supplier_ref = '0'
        suppliers = record.seller_ids
        if suppliers:
            supplier = suppliers[0]
            supplier_product_code = supplier.product_code or ''
            supplier_ref = supplier.name.ref or '0'
        return {'Gesarc': supplier_product_code,
                'Gesfou': supplier_ref,
                # "fabricant" could maybe be removed
                'Cplz25': supplier_ref,
                }

    @mapping
    def category_warnings(self, record):
        cat = record.categ_id
        return {
            'Warceg': cat.with_context({'lang': 'de_DE'}).warning_info or '',
            'Warcfr': cat.with_context({'lang': 'fr_BE'}).warning_info or '',
            'Warcnl': cat.with_context({'lang': 'nl_BE'}).warning_info or '',
            }

    @mapping
    def fixed_fields(self, record):
        """ return hardcoded values for fields """
        zero = ('Cp2z17', 'Cp2z19')
        values = {f: 0 for f in zero}
        return values

    @mapping
    def temporary_fixed_field(self, record):
        """ This is to help testing before resolution of ALCN-1456."""
        return {'Gescov': 0}

    @mapping
    def group_and_subgroup(self, record):
        """The group and sub group of the product.

        The sub group is the group in which the product is.
        The group is the parent group of the sub group

        """
        sub_grp = record.categ_id
        if sub_grp.is_business_unit or not sub_grp.parent_id:
            grp = sub_grp
        else:
            grp = sub_grp.parent_id
        grp_ref = grp.esb_ref or '0'
        subgrp_ref = sub_grp.esb_ref or '0'
        return {
            'Gescgr': grp_ref if grp_ref.isdigit() else '0',
            'Gescsg': subgrp_ref if subgrp_ref.isdigit() else '0',
            }

    @mapping
    def business_unit(self, record):
        unit_ref = ''
        category = record.categ_id
        while category:
            if category.is_business_unit:
                unit_ref = category.esb_ref
                break
            else:
                category = category.parent_id
        return {'Cplz14': unit_ref or ''}

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
    def product_given(self, record):
        return {'Cp2z22': record.additional_product_id.default_code or ''}


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
