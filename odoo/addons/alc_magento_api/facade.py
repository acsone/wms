# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import uuid

import dicttoxml
import xmltodict

from odoo import fields

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext


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
            "backorders_cancelled": FacadeBackorders,
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

    def _get_parser_product(self):
        discounts = (
            "supplier_discount_ids",
            ["discount_sale:promotion", "date_end:promotion_valid_until"],
        )
        promotions = (
            "supplier_promotion_ids",
            ["ratio_display_name:promotion", "date_end:promotion_valid_until"],
        )
        parser = [
            "default_code:Reference",
            "name:Article",
            ("categ_ids", ["id", "name:Mot_Cle"]),
            ("manufacturer", ["name:Fabricant"]),
            "cnk_code:Code_national",
            "indicated_price:Prix_Vente_Indicatif",
            "name:Article",
            "vat:TVA",
            "barcode:ean_13",
            "code_cti:ext_cti",
            ("shopinvader_bind_ids", [("lang_id", ["code"]), "url_key"]),
        ]
        if self.partner.supplier_promotion_sale_allowed:
            parser += [discounts, promotions]
        return parser

    def _json_for_xml(self, lang, data, record):
        urls_shop = data.pop("shopinvader_bind_ids")
        urls = {u["lang_id"]["code"]: u["url_key"] for u in urls_shop}
        data["url"] = urls.get(lang or "fr_BE")  # product not on website anymore
        categ = None
        categ_ids = data.pop("categ_ids")
        if categ_ids:
            categ = self.env["product.category"].browse(categ_ids[-1].pop("id"))
            data.update(categ_ids[-1])
        else:
            data["Mot_Cle"] = None
        price_key = self.partner.property_product_pricelist.role_name
        price_gross = record._price_cache_get(price_key)["price"]
        vat = float(data["TVA"].replace("%", "")) if data["TVA"] else 0
        price_net = round(price_gross * (1 + vat / 100), 2)  # round for EUR
        data["Prix_Brut_HTVA_EUR"] = price_gross
        data["Prix_Brut_TVAC_EUR"] = price_net
        if self.partner.supplier_promotion_sale_allowed:
            discounts = data.pop("supplier_discount_ids")
            for discount in discounts:
                discount["promotion"] = "%s%%" % discount["promotion"]
            promotions = data.pop("supplier_promotion_ids")
            data["promotions"] = discounts + promotions
        data["Article_EN"] = record.with_context(lang="en_US").name
        data["Article_NL"] = record.with_context(lang="nl_BE").name
        categ_en = categ.with_context(lang="en_US").name if categ else None
        data["Categorie_EN"] = categ_en
        categ_nl = categ.with_context(lang="nl_BE").name if categ else None
        data["Categorie_NL"] = categ_nl
        return data


class FacadeCatalog(FacadeProduct):
    usage = "catalog"

    def process_kwargs(self, **kwargs):
        langs = {"en": "en_US", "fr": "fr_BE", "nl": "nl_BE"}
        kwargs["lang"] = langs[kwargs.pop("language").lower()]
        return kwargs

    def apply(self, **kwargs):
        return self.service._search(limit=10, **kwargs)  # TODO: REMOVE

    def process_result(self, result, **kwargs):
        lang = kwargs.pop("lang")
        records = result.with_context(lang="fr_BE")
        parser = self._get_parser_product()
        records_json = records.jsonify(parser)
        data = [self._json_for_xml(lang, j, r) for j, r in zip(records_json, result)]
        return self._json_to_xml(data, custom_root="catalog")


class FacadePriceList(FacadeProduct):
    usage = "sale_statistics"

    def apply(self, **kwargs):
        return self.service._get_top_ordered(**kwargs)

    def process_result(self, result, **kwargs):
        ids = [r["product_id"] for r in result["data"]]
        records = self.env["product.product"].with_context(lang="fr_BE").browse(ids)
        parser = self._get_parser_product()
        records_json = records.jsonify(parser)
        data = [self._json_for_xml(None, j, r) for j, r in zip(records_json, records)]
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
        for item in items:
            item["date_cancelled"] = date_cancelled
            item.update(item.pop("product_id"))
        return data, items

    def process_result(self, result, **kwargs):
        parser = self._get_parser()
        data = []
        for r in result.jsonify(parser):
            data += self._json_for_xml(r)
        xmls = [self._json_to_xml(d, root=False) for d in data]
        return self.wrap_xml("backorders_cancelled", "order", xmls)

    def _get_parser(self):
        parser_move_lines = [
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
        country_dict = partner_dict.pop("country_id")
        partner_dict["country"] = country_dict["name"]
        data.update(partner_dict)
        for item in data["items"]:
            item.update(item.pop("product_id"))
            lots = item.pop("lot_ids")
            if lots:  # we should not need to drop other lots in future versions
                item.update(lots[0])
            if item.get("peremption"):
                item["peremption"] = self._datetime_to_date(item["peremption"])
            item["prix_brut_htva"] = item["prix_net_htva"]
        data["date"] = self._datetime_to_date(data["date"])
        return data

    def process_result(self, result, **kwargs):
        parser = self._get_parser()
        records_json = result.jsonify(parser)
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
            "product_qty:qty",
            "price_unit:prix_net_htva",
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


class FacadeShopinvaderCart(Facade):
    usage = "cart"
    collection = "shopinvader.api.v2"

    def apply(self, **kwargs):
        self.service.update(**kwargs["info"])
        return self.service.sync(**kwargs["sync"])

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
        for line_xml in quote_dict.pop("item", []):
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
            "date_order_short",
            "client_order_ref",
            ("order_line:lines", parser_lines),
        ]
