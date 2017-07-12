# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SpecialPromotionExportMapper(Component):
    _name = 'esb.special.promotion.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.pricelist.item'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and
                    work.timestamp.kind == 'special.promotion')

    @mapping
    def compute_sku(self, record):
        sku = ''
        if record.product_tmpl_id:
            sku = record.product_tmpl_id.default_code
        elif record.product_id:
            sku = record.product_id.default_code
        return {'Sku': sku}

    @mapping
    def compute_percent(self, record):
        percent = '0.00'
        if record.percent_price:
            percent = '{0:.2f}'.format(record.percent_price)
        return {'Percent': percent}

    @mapping
    def compute_startdate(self, record):
        if record.date_start:
            return {'StartDate': record.date_start.replace('-', '')}
        else:
            return {'StartDate': ''}

    @mapping
    def compute_enddate(self, record):
        if record.date_end:
            return {'EndDate': record.date_end.replace('-', '')}
        else:
            return {'EndDate': ''}

    @mapping
    def compute_checksum(self, record):
        # TODO : what is it computed on ?
        return {}

    @mapping
    def compute_fixed_values(self, record):
        return {
                'AlcyonGroupId': '', # Not implemented in the new context
                'Action': 'Create',
                }


class SpecialPromotionCronExporter(Component):

    _name = 'esb.special.promotion.cron.exporter'
    _inherit = ['esb.cron.exporter', ]
    _usage = 'record.exporter.cron'
    _apply_on = 'product.pricelist.item'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp
                    and work.timestamp.kind == 'special.promotion')

    def get_items_domain(self):
        # As the doc only deal with this type...
        return [('compute_price', '=', 'percentage')]

    def create_record(self, items):
        """
            For all item in a pricelist add an entry for
            each client it applies on
        """
        prepared = []
        for item in items:
            customers = self.env['res.partner'].search(
                [('discount_pricelist_id', '=', item.pricelist_id.id)])
            map_record = self.mapper.map_record(item)
            for cust in customers:
                map_record.update(CustomerId=cust.ref)
                prepared.append(map_record.values())
        return prepared
