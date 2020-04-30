# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from ...components.mapper import dt2nakeddate, falsy2zero


class BuyXGetYExportMapper(Component):
    _name = 'esb..buyx.gety.mapper'
    _inherit = ['esb.export.mapper']
    _apply_on = 'product.supplierinfo.esbflux'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'buyx.gety')

    direct = [
        (falsy2zero('ratio_main_product'), 'QtyBuy1'),
        (falsy2zero('ratio_promotional_product'), 'QtyGet1'),
        (dt2nakeddate('date_start'), 'StartDate'),
        (dt2nakeddate('date_end'), 'EndDate'),
    ]

    @mapping
    def compute_sku(self, record):
        return {'Sku': record.product_tmpl_id.default_code or ''}

    @mapping
    def compute_alcyongroup(self, record):
        return {'AlcyonGroupId': self.options.alcyon_group_id}

    @mapping
    def compute_action(self, record):
        return {'Action': record.action.capitalize()}

    @mapping
    def compute_fixed_value(self, record):
        return {
            'QtyBuy2': 0,
            'QtyGet2': 0,
            'QtyBuy3': 0,
            'QtyGet3': 0,
            'QtyBuy4': 0,
            'QtyGet4': 0,
            'QtyBuy5': 0,
            'QtyGet5': 0,
            'QtyBuy6': 0,
            'QtyGet6': 0,
        }

    @mapping
    def compute_checksum(self, record):
        checksum = ''.join(
            [str(record.real_id), self.options.alcyon_group_id, 'buyxgety']
        )
        return {'CheckSum': checksum}


class BuyXGetYCronExporter(Component):

    _name = 'esb.buyx.gety.cron.exporter'
    _inherit = ['esb.cron.exporter']
    _usage = 'record.exporter.cron'
    _apply_on = 'product.supplierinfo.esbflux'

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == 'buyx.gety')

    def _prepare_item(self, items):
        """ For each promotion, multiple items are needed.

        One item for each Alyon Group with an esb_ref equal or higher to 100
        """
        prepared = []
        items = items.remove_duplicate_actions()
        price_list = self.env['product.pricelist'].search(
            [('esb_ref', '!=', '')]
        )
        price_list = price_list.filtered(lambda r: len(r.esb_ref) > 2)
        alcyon_category_ids = price_list.mapped(lambda r: r.esb_ref)
        for item in items:
            for category in alcyon_category_ids:
                prepared.append(
                    self.mapper.map_record(item).values(
                        alcyon_group_id=category
                    )
                )
        return prepared

    def get_items_domain(self):
        """ Get only entries which are for now and the future """
        today = fields.Date.today()
        return [
            ('date_start', '!=', False),
            ('date_end', '>=', today),
            ('ratio_main_product', '!=', False),
            ('ratio_promotional_product', '!=', False),
            ('flux', '=', 'buyxgety'),
        ]
