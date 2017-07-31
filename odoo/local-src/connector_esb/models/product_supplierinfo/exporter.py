# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SpecialPromotionExportMapper(Component):
    _name = 'esb.special.promotion.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.supplierinfo'

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
        percent = 0
        if record.discount_sale:
            percent = record.discount_sale
        return {'Percent': '{0:.2f}'.format(percent)}

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
                'AlcyonGroupId': '',  # Not implemented in new context
                'Action': 'Create',   # Fixed value !?
                }


class SpecialPromotionCronExporter(Component):

    _name = 'esb.special.promotion.cron.exporter'
    _inherit = ['esb.cron.exporter', ]
    _usage = 'record.exporter.cron'
    _apply_on = 'product.supplierinfo'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp)

    def get_items_domain(self):
        return []
