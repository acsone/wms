# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PromotionAlcyonExportMapper(Component):
    _name = 'esb..promotion.alcyon.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.pricelist.item'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and
                    work.timestamp.kind == 'promotion.alcyon')

    @mapping
    def compute_alcyongroup(self, record):
        group_id = ''
        if record.pricelist_id:
            group_id = (record.pricelist_id.esb_ref or '')
        return {'AlcyonGroupId': group_id}

    @mapping
    def compute_percent(self, record):
        percent = '0.00'
        if record.percent_price:
            percent = '{0:.2f}'.format(record.percent_price)
        return {'Percent': percent}

    @mapping
    def compute_action(self, record):
        if record.price_category_id:
            return {'ProductType': record.price_category_id.name}


class SpecialPromotionCronExporter(Component):

    _name = 'esb.promotion.alcyon.cron.exporter'
    _inherit = ['esb.cron.exporter', ]
    _usage = 'record.exporter.cron'
    _apply_on = 'product.pricelist.item'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp
                    and work.timestamp.kind == 'promotion.alcyon')

    def get_items_domain(self):
        return [('applied_on', '=', '2b_product_price_category')]
