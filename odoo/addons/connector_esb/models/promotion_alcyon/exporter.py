# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class PromotionAlcyonExportMapper(Component):
    _name = "esb..promotion.alcyon.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "product.pricelist.item"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "promotion.alcyon")

    @mapping
    def compute_alcyongroup(self, record):
        return {"AlcyonGroupId": record.pricelist_id.esb_ref or ""}

    @mapping
    def compute_percent(self, record):
        percent = "0.00"
        if record.percent_price:
            percent = "{:.2f}".format(record.percent_price)
        return {"Percent1": percent, "Percent2": "0"}

    @mapping
    def compute_product_type(self, record):
        """ Compute product type.

        For a promotion on all other product the price_category_id is empty
        But the content of the node in xml must be seven <space> char.

        In the historical xml file sent by the AS400 to the ESB the xml node
        <ProductType> is empty but contains a <CR> so with the file indentation
        it is interpreted by the ESB/Magento as seven spaces.
        Without the same behaviour an existing promotion was not replaced and
        two promotion on all other prodcut became present.
        """
        product_type = "       "
        if record.price_category_id:
            product_type = record.price_category_id.name or ""
        return {"ProductType": product_type}


class SpecialPromotionCronExporter(Component):

    _name = "esb.promotion.alcyon.cron.exporter"
    _inherit = ["esb.cron.exporter"]
    _usage = "record.exporter.cron"
    _apply_on = "product.pricelist.item"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "promotion.alcyon")

    def get_items_domain(self):

        return [
            ("applied_on", "in", ["2b_product_price_category", "3_global"]),
            ("percent_price", "!=", 0),
        ]
