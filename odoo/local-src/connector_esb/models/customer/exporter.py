# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from ...components.mapper import falsy2zero


class CustomerExportMapper(Component):
    _name = 'esb.customer.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'res.partner'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'customer')

    direct = [
        ('email', 'Email'),
        ('name', 'Firstname'),
        ('is_price_on_labels', 'MsrpSticker'),
        ('ref', 'ErpId'),
        (falsy2zero('time_limit_order'), 'IdRound')
    ]

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
    def compute_back_order(self, record):
        return {
            'BackordersEnable': int(record.is_sale_back_order_accepted)
        }

    @mapping
    def compute_activitytype(self, record):
        val = {}
        for r in record.category_id:
            val[r.name.replace(' ', '_')] = "Y"
        return val

    @mapping
    def compute_alcyongroupid(self, record):
        if record.discount_pricelist_id:
            return {'AlcyonGroupId': record.discount_pricelist_id.esb_ref}
        else:
            return {'AlcyonGroupId': ''}

    @mapping
    def compute_groupid(self, record):
        if record.alcyon_category_id:
            return {'GroupId': record.alcyon_category_id.esb_ref}
        else:
            return {'GroupId': ''}

    @mapping
    def compute_iddelegate(self, record):
        if record.user_id:
            return {'IdDelegate': record.user_id.esb_ref}
        else:
            return {'IdDelegate': ''}

    @mapping
    def compute_pharmacy(self, record):
        if record.pharmacist_id:
            return {'IdPharmacy': record.pharmacist_id.ref}
        else:
            return {'IdPharmacy': ''}

    @mapping
    def compute_optional(self, record):
        """Compute direct but optional value"""
        return {'DepositNumber': record.vet_depot_number or ''}

    @mapping
    def compute_taxcode(self, record):
        value = 1 if record.vat else 0
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
        return {
                'Username': '',
                'Password': '',
                'WebsiteId': '',
                'StoreId': '',
                'IsActive': '',
                'ShowTimer': True,
                'Lapsing': False,
                'LapsingDuration': 0,
                }

    @mapping
    def compute_language(self, record):
        lang = self.env['res.lang'].search([('code', '=', record.lang)],
                                           limit=1)
        return {
            # FR is the default value
            'Language': lang.esb_ref or 'FR',
        }

    @mapping
    def compute_onlinepayment(self, record):
        return {'OnlinePayment': 0}


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
        return [('customer', '=', True), ('parent_id', '=', False)]
