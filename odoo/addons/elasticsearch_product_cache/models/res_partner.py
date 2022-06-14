# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):

    _inherit = "res.partner"

    def _get_es_fields(self):
        self.ensure_one()
        price_key = self.property_product_pricelist.role_name
        discount_key = self.discount_pricelist_id.discount_role_name
        fields = [
            "objectID",
            "name",
            "sku",
            "cnk_code",
            "barcode",
            "code_cti",
            "url_key",
            "categories.name",
            "categories.level",
            "price.%s" % price_key,
            "price.%s" % discount_key,
            "indicated_price",
            "manufacturer.name",
            "vat.amount",
            "specials",
        ]
        if self.supplier_promotion_sale_allowed:
            fields += [
                "supplier_promotion.ratio_main_product",
                "supplier_promotion.date_start",
                "supplier_promotion.date_end",
                "supplier_discount.discount_sale",
                "supplier_discount.date_start",
                "supplier_discount.date_end",
            ]
        return fields

    def _get_es_fields_translations(self):
        self.ensure_one()
        return [
            "objectID",
            "name",
            "url_key",
            "categories.name",
            "categories.level",
            "manufacturer.name",
        ]

    def _get_shop_products(self, langs=None, ids=None):
        self.ensure_one()
        product_model = self.env["product.product"]
        es_params = {}
        es_params["source"] = self._get_es_fields()
        q = {"bool": {"must": [{"term": {"allowed_partner_types": self.partner_type}}]}}
        if self.partner_type == "supplier":
            q = {"bool": {"must": [{"term": {"supplier_id": self.id}}]}}
        if ids:
            q["bool"]["must"].append({"terms": {"_id": ids}})
        es_params["query"] = q
        params = {"size": 10000}
        records = product_model._get_products_from_es_cache(
            es_params=es_params, params=params
        )
        translations = {}
        es_params["source"] = self._get_es_fields_translations()
        for lang_code in langs or ["nl_BE", "fr_BE"]:
            translations[lang_code] = product_model._get_products_from_es_cache(
                lang_code=lang_code, es_params=es_params, params=params
            )
        return records, translations
