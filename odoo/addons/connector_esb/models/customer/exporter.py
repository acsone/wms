# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from ...components.mapper import falsy2emptystring


class CustomerExportMapper(Component):
    _name = 'esb.customer.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'res.partner'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'customer')

    direct = [
        (falsy2emptystring('email'), 'Email'),
        (falsy2emptystring('ref'), 'ErpId'),
    ]

    @mapping
    def compute_firstname(self, record):
        try:
            name = record.name_get()[0][1]
        except TypeError:
            name = record.name
        return {'Firstname': name or ''}

    @mapping
    def compute_statistic_code(self, record):
        code = ''
        pricelist = record.property_product_pricelist
        if pricelist == self.env.ref('specific_data.product_pricelist_pb1'):
            code = '10'
        elif pricelist == self.env.ref('specific_data.product_pricelist_pb2'):
            code = '60'
        return {'StatisticCode': code}

    @mapping
    def compute_idround(self, record):
        """ Adapt the value of time_limit_order.

        The value is in float format but the minutes on a base of 100
        """
        tlo = record.time_limit_order
        hours = int(tlo)
        minutes = int((tlo - hours) * 100) * 60 / 100
        value = '{:02d}{:02d}'.format(hours, minutes)
        return {'IdRound': value}

    @mapping
    def compute_activitytype(self, record):
        val = {}
        for r in record.category_id:
            val[r.name.replace(' ', '_')] = "Y"
        return val

    @mapping
    def compute_alcyongroupid(self, record):
        esb_ref = ''
        if record.discount_pricelist_id:
            esb_ref = record.discount_pricelist_id.esb_ref
        return {'AlcyonGroupId': esb_ref or ''}

    @mapping
    def compute_groupid(self, record):
        esb_ref = ''
        if record.alcyon_category_id:
            esb_ref = record.alcyon_category_id.esb_ref
        return {'GroupId': esb_ref or ''}

    @mapping
    def compute_iddelegate(self, record):
        esb_ref = ''
        if record.user_id:
            esb_ref = record.user_id.esb_ref
        return {'IdDelegate': esb_ref or ''}

    @mapping
    def compute_pharmacy(self, record):
        if record.pharmacist_id:
            return {'IdPharmacy': record.pharmacist_id.ref or ''}
        else:
            return {'IdPharmacy': ''}

    @mapping
    def compute_optional(self, record):
        """Compute direct but optional value"""
        return {'DepositNumber': record.vet_depot_number or ''}

    @mapping
    def compute_taxcode(self, record):
        value = 1
        if record.vat:
            country = record.vat[:2]
            if country == 'BE':
                value = 0
            else:
                value = 3
        return {'TaxCode': value}

    @mapping
    def compute_taxvat(self, record):
        if record.vat:
            return {'Taxvat': record.vat.replace('.', '').replace(' ', '')}

    @mapping
    def compute_serialno(self, record):
        return {'SerialNo': record.last_suite_name or 0}

    @mapping
    def compute_empty_ones_or_default(self, record):
        return {'ShowTimer': True}

    @mapping
    def compute_language(self, record):
        lang = self.env['res.lang'].search(
            [('code', '=', record.lang)], limit=1
        )
        return {
            # FR is the default value
            'Language': lang.esb_ref
            or 'FR'
        }

    @mapping
    def compute_onlinepayment(self, record):
        return {'OnlinePayment': False}

    @mapping
    def compute_freeshipping(self, record):
        return {'FreeShipping': not record.help_with_fee}


class CustomerCronExporter(Component):

    _name = 'esb.customer.cron.exporter'
    _inherit = 'esb.cron.exporter'
    _usage = 'record.exporter.cron'
    _apply_on = 'res.partner'

    _mark_as_exported = True

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'customer')

    def get_items_domain(self):
        return [('customer', '=', True), ('email', '<>', False)]
