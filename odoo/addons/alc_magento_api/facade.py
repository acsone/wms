# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import uuid

import dicttoxml
import xmltodict

from odoo import fields

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext

LANGS = {"en": "en_US", "fr": "fr_BE", "nl": "nl_BE"}
LANGS_INVERSE = {"en_US": "en", "fr_BE": "fr", "nl_BE": "nl"}

_logger = logging.getLogger(__name__)


class Facade(object):
    collection = "shopinvader.backend"

    @staticmethod  # factory method
    def factory(env, partner, service_name):
        return Facade._get_service_class(service_name)(env, partner)

    @staticmethod
    def _get_service_class(service_name):
        return {
            "quote": FacadeQuote,
            "quote-csv": FacadeQuoteCsv,  # TODO: endpoint?
            "cancelled_backorder": FacadeBackorders,
            "packing-slip": FacadePackingSlip,
            "price-list": FacadePriceList,
            "catalog": FacadeCatalog,
            "sales_order": FacadeOrder,
        }[service_name]

    def _get_odoo_service(self):
        partner = self.partner
        context = dict(partner._context, authenticated_partner_id=partner.id)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=_PseudoCollection(self.collection, self.env(context=context)),
            authenticated_partner_id=partner.id,
        )
        return work.component(usage=self.usage)

    def __init__(self, env, partner):
        self.env = env
        self.partner = partner
        self.service = self._get_odoo_service()
        self.errors = []
        self.location = None

    def process_kwargs(self, **kwargs):
        return kwargs

    def apply(self, **kwargs):
        raise NotImplementedError

    def process_result(self, result, **kwargs):
        return result

    def wrap_result(self, result, **kwargs):
        errors = self.process_errors(result, **kwargs)
        return result, errors, self.location

    def process_errors(self, result, **kwargs):
        return self.errors

    def __call__(self, **kwargs):
        function_args = self.process_kwargs(**kwargs)
        service_result = self.apply(**function_args)
        result = self.process_result(service_result, **function_args)
        return self.wrap_result(result, **kwargs)

    def _xml_to_json(self, xml):
        return xmltodict.parse(xml)

    def _json_to_xml(self, data, **kwargs):
        return dicttoxml.dicttoxml(data, attr_type=False, **kwargs)

    @staticmethod
    def _datetime_to_date(ds):
        return fields.Date.to_string(fields.Date.from_string(ds))

    @staticmethod
    def wrap_xml(root, element, xml_by_pairs):
        result = '<?xml version="1.0" encoding="UTF-8" ?><%s>' % root
        iterator = iter(xml_by_pairs)
        for first, second in zip(iterator, iterator):
            result += "<{e}>{f}{s}</{e}>".format(e=element, f=first, s=second)
        return result + ("</%s>" % root)


class FacadeProduct(Facade):
    def apply(self, **kwargs):
        raise NotImplementedError

    def __init__(self, env, partner):
        super(FacadeProduct, self).__init__(env, partner)
        self.today = fields.Date.today()

    def _get_cache_price_key(self, price_cache, key, discount=False):
        item_list = price_cache[key]
        if len(item_list) == 1:
            item = item_list[0]
        else:
            filter_dates = lambda x: (
                not x["date_start"] or x["date_start"] <= self.today
            ) and (not x["date_end"] or x["date_end"] >= self.today)
            candidates = filter(filter_dates, item_list)
            if candidates:
                item = min(candidates, key=lambda it: it["date_start"] or self.today)
            else:
                item = {"discount": 0} if discount else {"price": 0}
        return item["discount"] if discount else item["price"]

    def _get_cache_price(self, price_cache, price_key, discount_key):
        price = self._get_cache_price_key(price_cache, price_key)
        # if discount_key:
        #     discount = self._get_cache_price_key(price_cache, discount_key, True)
        #     price = round(price - (price * discount / 100), 2)
        return price

    def _get_cache_category(self, categories):
        return categories[-1]["name"] if categories else None

    def _json_for_xml_from_cache(self, lang, records_translations):
        records, translations = records_translations
        json_by_id = {}
        urls = {}
        price_key = self.partner.property_product_pricelist.role_name
        discount_key = self.partner.discount_pricelist_id.discount_role_name
        for record in records:
            record_id = record.pop("objectID")
            vat = record.get("vat", {"amount": 21})["amount"]  # TODO
            json_by_id[record_id] = {
                "Article_EN": record["name"],
                "Reference": record["sku"],
                "Code_national": record["cnk_code"],
                "TVA": vat,
                "Prix_Vente_Indicatif": record["indicated_price"],
                "ean_13": record["barcode"],
                "ext_cti": record["code_cti"],
            }
            urls[record_id] = {"en_US": record["url_key"]}
            price = self._get_cache_price(record["price"], price_key, discount_key)
            price_with_vat = round(price + price * vat / 100, 2)
            json_by_id[record_id]["Prix_Brut_HTVA_EUR"] = price
            json_by_id[record_id]["Prix_Brut_TVAC_EUR"] = price_with_vat
            if self.partner.supplier_promotion_sale_allowed:
                promotions = []
                for discount in record.get("supplier_discount", []):
                    discount = {
                        "promotion": discount["discount_sale"],
                        "promotion_valid_until": discount["date_end"],
                    }
                    promotions.append(discount)
                for promotion in record.get("supplier_promotion", []):
                    # TODO: add ratio_main_product to output?
                    promotion = {
                        "promotion": "FREE products",
                        "promotion_valid_until": promotion["date_end"],
                    }
                    promotions.append(promotion)
                json_by_id[record_id]["promotions"] = promotions
        for record in translations["nl_BE"]:
            record_id = record.pop("objectID")
            record_json = json_by_id[record_id]
            categories = record.get("categories", [])
            record_json["Article_NL"] = record["name"]
            record_json["Categorie_NL"] = self._get_cache_category(categories)
            urls[record_id]["nl_BE"] = record["url_key"]
        for record in translations["fr_BE"]:
            record_id = record.pop("objectID")
            record_json = json_by_id[record_id]
            categories = record.get("categories", [])
            record_json["Mot_Cle"] = self._get_cache_category(categories)
            record_json["Article"] = record["name"]
            urls[record_id]["fr_BE"] = record["url_key"]
            record_json["Fabricant"] = record.get("manufacturer", {}).get("name")
        for record_id in urls:
            url_suffix = urls[record_id][lang]
            lang_slug = LANGS_INVERSE[lang]
            url = "https://www.alcyonbelux.be/{}/{}".format(lang_slug, url_suffix)
            json_by_id[record_id]["url"] = url
        return json_by_id


class FacadeCatalog(FacadeProduct):
    usage = "catalog"

    def process_kwargs(self, **kwargs):
        kwargs["lang"] = LANGS[kwargs.pop("language").lower()]
        return kwargs

    def apply(self, **kwargs):
        return self.partner._get_shop_products()

    def process_result(self, result, **kwargs):
        lang = kwargs.pop("lang")
        json_by_id = self._json_for_xml_from_cache(lang, result)
        return self._json_to_xml(json_by_id.values(), custom_root="catalog")


class FacadePriceList(FacadeProduct):
    usage = "sale_statistics"

    def apply(self, **kwargs):
        return self.service._get_top_ordered(**kwargs)

    def process_result(self, result, **kwargs):
        ids = [r["product_id"] for r in result["data"]]
        if not ids:
            self.errors = "<error>No bought product has been found</error>"
            return None
        records_data = self.partner._get_shop_products(ids=ids)
        json_by_id = self._json_for_xml_from_cache("en_US", records_data)
        data = (json_by_id[rid] for rid in ids if rid in json_by_id)
        return self._json_to_xml(data, custom_root="price_list")


class FacadeBackorders(Facade):
    usage = "pickings"

    def process_kwargs(self, **kwargs):
        from_date = kwargs.pop("date_cancelled", None)
        kwargs["from_date"] = from_date
        return kwargs

    def apply(self, **kwargs):
        return self.service._search_canceled(**kwargs)

    def _json_for_xml(self, data):
        date_cancelled = self._datetime_to_date(data.pop("date_cancelled"))
        items = data.pop("items")
        items = [i for i in items if i.get("state") == "cancel"]
        for item in items:
            item.pop("state", None)
            item["date_cancelled"] = date_cancelled
            item.update(item.pop("product_id"))
        return data, items

    def process_result(self, result, **kwargs):
        if not result:
            self.errors = "<error>No cancelled backorder in this range</error>"
            return None
        parser = self._get_parser()
        data = []
        for r in result.jsonify(parser):
            data += self._json_for_xml(r)
        xmls = [self._json_to_xml(d, root=False) for d in data]
        return self.wrap_xml("backorders_cancelled", "order", xmls)

    def _get_parser(self):
        parser_move_lines = [
            "state",
            "product_qty:qty_ordered",
            "remaining_qty:qty_cancelled",
            ("product_id", ["default_code:sku"]),
        ]
        return [
            "id:internal_order_id",
            "date_done:date_cancelled",
            ("move_lines:items", parser_move_lines),
        ]


class FacadePackingSlip(Facade):
    usage = "pickings"

    def process_kwargs(self, **kwargs):
        kwargs["from_date"] = kwargs.pop("date")
        return kwargs

    def apply(self, **kwargs):
        return self.service._search_done(**kwargs)

    @staticmethod
    def _item_func(parent):
        return "note" if parent == "packing_slip" else "item"

    def _json_for_xml(self, data):
        partner_dict = data.pop("partner_id")
        if not partner_dict:
            _logger.exception("Magento API packing data: %s", data)
        country_dict = partner_dict.pop("country_id")
        partner_dict["country"] = country_dict["name"]
        data.update(partner_dict)
        data["items"] = [i for i in data["items"] if i.get("state") != "cancel"]
        for item in data["items"]:
            item.pop("state", None)
            item.update(item.pop("product_id"))
            lots = item.pop("lot_ids")
            if lots:  # we should not need to drop other lots in future versions
                item.update(lots[0])
            else:
                item["lot"] = None
            if item.get("peremption"):
                item["peremption"] = self._datetime_to_date(item["peremption"])
            else:
                item["peremption"] = None
            # TVA is from vat, which is a related to the name (e.g. 21%)
            tva = item["tva"]
            item["tva"] = tva[:-1] if isinstance(tva, (str, unicode)) else tva
        data["date"] = self._datetime_to_date(data["date"])
        return data

    def process_result(self, result, **kwargs):
        parser = self._get_parser()
        if not result:
            self.errors = "<error>no packing slips have been found</error>"
            return None
        records_json = result.jsonify(parser)
        _logger.info("Magento API packing Args: %s", result.ids)
        return self._json_to_xml(
            [self._json_for_xml(r) for r in records_json],
            custom_root="packing_slip",
            item_func=self._item_func,
        )

    def _get_parser(self):
        parser_partner = [
            "name",
            "email",
            "street:address",
            "city:locality",
            ("country_id", ["name"]),
        ]
        parser_product = ["default_code:reference", "name:article", "vat:tva"]
        parser_lot = ["name:lot", "expiry_date:peremption"]
        parser_move_lines = [
            "name",
            "state",
            "product_qty:qty",
            ("prix_net_htva", self._get_price_from_move),
            ("prix_brut_htva", self._get_price_from_move),
            "serial_number:numero_de_suite",
            ("product_id", parser_product),
            ("lot_ids", parser_lot),
        ]
        return [
            "id:ne_id",
            "date_done:date",
            ("partner_id", parser_partner),
            ("move_lines:items", parser_move_lines),
        ]

    def _get_price_from_move(self, stock_move, field_name):
        if field_name == "prix_net_htva":
            return stock_move.order_line_id.price_reduce
        if field_name == "prix_brut_htva":
            return stock_move.order_line_id.price_unit
        return 0.0


class FacadeShopinvaderCart(Facade):
    usage = "cart"
    collection = "shopinvader.api.v2"

    def apply(self, **kwargs):
        self.service.update(**kwargs["info"])
        self.service.sync(**kwargs["sync"])  # return None

    def _get_product_by_sku(self, sku):
        domain = self.env["product.product"].get_partner_type_domain(self.partner)
        domain.append(("default_code", "=", sku))
        return self.env["product.product"].search(domain, limit=1)

    def __init__(self, env, partner):
        super(FacadeShopinvaderCart, self).__init__(env, partner)

        backend = self.env.ref("alc_eshop.backend")
        setattr(self.service.work, "shopinvader_backend", backend)

        location_param = "alc_magento_api.cart_location"
        self.location = self.env["ir.config_parameter"].get_param(location_param)

    def process_errors(self, result, **kwargs):
        error = None
        if len(self.errors) == 1:
            error = "<error>The product %s is not available</error>" % self.errors[0]
        elif len(self.errors) > 1:
            missing = ", ".join(self.errors)
            error = "<error>The products %s are not available</error>" % missing
        return error


class FacadeQuote(FacadeShopinvaderCart):
    def process_kwargs(self, **kwargs):
        quote_xml = kwargs.pop("data")
        quote_dict = self._xml_to_json(quote_xml)["quote"]

        lines = []
        items = quote_dict.pop("item", [])
        items = [items] if isinstance(items, dict) else items
        for line_xml in items:
            product = self._get_product_by_sku(line_xml["sku"])
            if product:
                qty = int(line_xml["qty"])
                line_id = str(uuid.uuid4())
                line = {"product_id": product.id, "qty": qty, "uuid": line_id}
                lines.append(line)
            else:
                self.errors.append(line_xml["sku"])
        kwargs["sync"] = {"transactions": lines}

        info = {}
        args_to_fields = {
            "comments": "note",
            "serial_number": "suite_name",
            "order_reference": "customer_ref",
        }
        for key in args_to_fields:
            if quote_dict.get(key):
                info[args_to_fields[key]] = quote_dict[key]
        kwargs["info"] = info

        return kwargs


class FacadeQuoteCsv(FacadeShopinvaderCart):
    def process_kwargs(self, **kwargs):
        quote_csv = kwargs.pop("file").read().split("\n")
        if not len(quote_csv) > 1:
            raise ValueError("Not enough lines.")  # ERROR

        lines = []
        for csv_line in [l for l in quote_csv[1:] if l]:
            sku, qty = csv_line.split(";")
            product = self._get_product_by_sku(sku)
            if product:
                line_id = str(uuid.uuid4())
                line = {"product_id": product.id, "qty": int(qty), "uuid": line_id}
                lines.append(line)
            else:
                self.errors.append(sku)
        kwargs["sync"] = {"transactions": lines}

        info = {}
        first_line = quote_csv[0].split(";")
        info["suite_name"] = first_line[0] or False
        info["client_order_ref"] = first_line[1] or False
        # "email": first_line[2]
        info["note"] = first_line[3] or False
        kwargs["info"] = info

        return kwargs


class FacadeOrder(Facade):
    usage = "orders"

    def process_kwargs(self, **kwargs):
        kwargs["from_date"] = kwargs.pop("since")
        return kwargs

    @staticmethod
    def _item_func(parent):
        return "order" if parent == "data" else "line"

    def apply(self, **kwargs):
        return self.service._search(**kwargs)

    def _json_for_xml(self, data):
        for line in data["lines"]:
            line.update(line.pop("product_id"))
        return data

    def process_result(self, result, **kwargs):
        parser = self._get_parser()
        if not result:
            self.errors = "<error>No orders found in this range.</error>"
            return None
        records_json = result.jsonify(parser)
        return self._json_to_xml(
            [self._json_for_xml(r) for r in records_json],
            custom_root="data",
            item_func=self._item_func,
        )

    def _get_parser(self):
        parser_lines = [
            "id:line_id",
            "product_qty:qty_ordered",
            "qty_delivered",
            "product_qty_canceled:qty_canceled",
            ("product_id", ["default_code:sku"]),
        ]
        return [
            "id:web_id",
            "name:erp_name",
            "suite_name",
            "date_order_short:date",
            "client_order_ref",
            ("order_line:lines", parser_lines),
        ]
