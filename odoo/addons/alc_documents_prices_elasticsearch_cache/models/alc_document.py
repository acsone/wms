# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class AlcDocument(models.Model):

    _inherit = "alc.document"

    def _get_cache_price_key(self, today, price_cache, key, discount=False):
        item_list = price_cache[key]
        if len(item_list) == 1:
            item = item_list[0]
        else:
            filter_dates = lambda x: (
                not x["date_start"] or x["date_start"] <= today
            ) and (not x["date_end"] or x["date_end"] >= today)
            candidates = filter(filter_dates, item_list)
            if candidates:
                item = min(candidates, key=lambda it: it["date_start"] or today)
            else:

                item = {"discount": 0} if discount else {"price": 0}
        return item["discount"] if discount else item["price"]

    def _get_cache_price(self, today, price_cache, price_key, discount_key):
        price = self._get_cache_price_key(today, price_cache, price_key)
        # if discount_key:
        #     discount = self._get_cache_price_key(today, price_cache, discount_key, True)
        #     price = round(price - (price * discount / 100), 2)
        return price

    def _get_cache_category(self, categories):
        return categories[-1]["name"] if categories else None

    def _get_cache_discount(self, today, discount_records):
        filter_dates = lambda x: (not x["date_start"] or x["date_start"] <= today) and (
            not x["date_end"] or x["date_end"] >= today
        )
        candidates = filter(filter_dates, discount_records)
        item = None
        if candidates:
            item = min(candidates, key=lambda it: it["date_start"] or today)
        return item

    def _get_products(self):
        # UNSAFE override! returns a [json] instead of the records!
        # does NOT call super
        today = fields.Date.today()
        records, translations = self.partner_id._get_shop_products()
        json_by_id = {}
        price_key = self.partner_id.property_product_pricelist.role_name
        discount_key = self.partner_id.discount_pricelist_id.discount_role_name
        for record in records:
            rid = record.pop("objectID")
            json_by_id[rid] = {"Reference": record["sku"]}
            if self.compute == "pricelist":
                vat = int(record.get("vat", {"amount": 21})["amount"] or 21)
                json_by_id[rid]["Article_EN"] = record["name"]
                json_by_id[rid]["Code_national"] = record["cnk_code"]
                json_by_id[rid]["TVA"] = "%s%%" % vat
                json_by_id[rid]["Prix_Vente_Indicatif"] = record["indicated_price"]
                json_by_id[rid]["ean_13"] = record["barcode"]
                json_by_id[rid]["ext_cti"] = record["code_cti"]
                categories = record.get("categories", [])
                json_by_id[rid]["Category_EN"] = self._get_cache_category(categories)
                json_by_id[rid]["Code_Mot_Cle"] = ""
                price = self._get_cache_price(
                    today, record["price"], price_key, discount_key
                )
                price_with_vat = round(price + price * vat / 100, 2)
                json_by_id[rid]["Prix_Brut_HTVA_EUR"] = price
                json_by_id[rid]["Prix_Brut_TVAC_EUR"] = price_with_vat
                json_by_id[rid]["Prix_Brut_TVAC_BEF"] = ""
            if self.compute == "discount":
                json_by_id[rid]["supplier_discount"] = record.get(
                    "supplier_discount", []
                )
                json_by_id[rid]["supplier_promotion"] = record.get(
                    "supplier_promotion", []
                )
                json_by_id[rid]["specials"] = record.get("specials", [])
        if self.compute == "pricelist":
            for record in translations["nl_BE"]:
                rid = record.pop("objectID")
                record_json = json_by_id[rid]
                record_json["Article_NL"] = record["name"]
                record_json["Article_DE"] = record["name"]  # TODO??? needs index
                categories = record.get("categories", [])
                record_json["Category_NL"] = self._get_cache_category(categories)
        for record in translations["fr_BE"]:
            rid = record.pop("objectID")
            record_json = json_by_id[rid]
            categories = record.get("categories", [])
            record_json["Mot_Cle"] = self._get_cache_category(categories)
            record_json["Article"] = record["name"]
            record_json["Fabricant"] = record.get("manufacturer", {}).get("name")
        return json_by_id.values()

    def _process_product_lines_pricelist(self, products, lines):
        # UNSAFE override! returns a [json] instead of the records!
        # does NOT call super
        keys = [field_parser["name"] for field_parser in self._get_lang_price_parser()]
        for product in products:
            lines.append([product[key] for key in keys])
        return lines

    def _process_product_lines_discount(self, products, lines):
        # UNSAFE override! returns a [json] instead of the records!
        # does NOT call super
        today = fields.Date.today()
        for product in products:
            for product_field in [
                "supplier_discount",
                "supplier_promotion",
                "specials",
            ]:
                records = product[product_field]
                _logger.debug(
                    "Decode %s for product %s with value %s",
                    product_field,
                    product,
                    records,
                )
                record = self._get_cache_discount(today, records)
                if record:
                    if product_field == "specials":
                        discount_type = u"Promotion spéciale"
                    elif product_field == "supplier_promotion":
                        discount_type = "Produits GRATUITS"  # TODO: rate?
                    else:
                        discount_type = "%s%% off" % record["discount_sale"]
                    date_end = fields.Date.from_string(record["date_end"])
                    line = [
                        product["Mot_Cle"],
                        product["Fabricant"],
                        product["Reference"],
                        product["Article"],
                        discount_type,
                        date_end.strftime("%d/%m/%Y") if date_end else "",
                    ]
                    lines.append(line)
        return lines
