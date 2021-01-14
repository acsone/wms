# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class SpecialPromotionExportMapper(Component):
    _name = "esb.special.promotion.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "product.supplierinfo.esbflux"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "special.promotion")

    @mapping
    def compute_sku(self, record):
        sku = ""
        if record.product_tmpl_id:
            sku = record.product_tmpl_id.default_code
        elif record.product_id:
            sku = record.product_id.default_code
        return {"Sku": sku or ""}

    @mapping
    def compute_percent(self, record):
        percent = 0
        if record.discount_sale:
            percent = record.discount_sale
        return {"Percent1": "{:.2f}".format(percent), "Percent2": "0"}

    @mapping
    def compute_startdate(self, record):
        if record.date_start:
            return {"StartDate": record.date_start.replace("-", "")}
        else:
            return {"StartDate": ""}

    @mapping
    def compute_enddate(self, record):
        if record.date_end:
            return {"EndDate": record.date_end.replace("-", "")}
        else:
            return {"EndDate": ""}

    @mapping
    def compute_alcyongroup(self, record):
        return {"AlcyonGroupId": self.options.alcyon_group_id}

    @mapping
    def compute_action(self, record):
        return {"Action": record.action.capitalize()}

    @mapping
    def compute_checksum(self, record):
        checksum = "".join(
            [str(record.real_id), self.options.alcyon_group_id, "special"]
        )
        return {"CheckSum": checksum}


class SpecialPromotionCronExporter(Component):

    _name = "esb.special.promotion.cron.exporter"
    _inherit = ["esb.cron.exporter"]
    _usage = "record.exporter.cron"
    _apply_on = "product.supplierinfo.esbflux"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "special.promotion")

    def _prepare_item(self, items):
        """ For each promotion, multiple items are needed.

        One item for each Alyon Group with an esb_ref equal or higher to 100
        """
        prepared = []
        items = items.remove_duplicate_actions()
        price_list = self.env["product.pricelist"].search([("esb_ref", "!=", "")])
        price_list = price_list.filtered(lambda r: len(r.esb_ref) > 2)
        alcyon_category_ids = price_list.mapped(lambda r: r.esb_ref)
        for item in items:
            for category in alcyon_category_ids:
                prepared.append(
                    self.mapper.map_record(item).values(alcyon_group_id=category)
                )
        return prepared

    def get_items_domain(self):
        """ Get only entries which are for now and the future """
        today = fields.Date.today()
        return [
            ("date_start", "!=", False),
            ("date_end", ">=", today),
            ("discount_sale", ">", 0),
            ("flux", "=", "specialpromotion"),
        ]
