# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime
import logging
import uuid

import dicttoxml
import pytz
import xmltodict
from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.alc_eshop_api_cart.schemas import CartUpdateRequest
from odoo.addons.alc_eshop_api_pickings.routers.pickings import (
    _search as search_pickings,
)
from odoo.addons.shopinvader_api_cart.schemas import CartSyncInput, CartTransaction

LANGS = {"en": "en_US", "fr": "fr_BE", "nl": "nl_BE"}
LANGS_INVERSE = {"en_US": "en", "fr_BE": "fr", "nl_BE": "nl"}

_logger = logging.getLogger(__name__)


class Facade:
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

    def __init__(self, env, partner):
        self.env = env
        self.partner = partner
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
        return dicttoxml.dicttoxml(data, attr_type=False, return_bytes=False, **kwargs)

    @staticmethod
    def _datetime_to_date(ds):
        return fields.Date.to_string(fields.Date.from_string(ds))

    @staticmethod
    def wrap_xml(root, element, xml_by_pairs):
        result = f'<?xml version="1.0" encoding="UTF-8" ?><{root}>'
        iterator = iter(xml_by_pairs)
        for first, second in zip(iterator, iterator, strict=True):
            result += f"<{element}>{first}{second}</{element}>"
        return result + (f"</{root}>")


class FacadeProduct(Facade):
    def apply(self, **kwargs):
        raise NotImplementedError

    def __init__(self, env, partner):
        super().__init__(env, partner)
        self.today = fields.Date.today()

    def _data_parser(self, include_amm=False):
        parser = [
            {"name": "Article_EN", "get": "name_en"},
            {"name": "Category_EN", "get": "categ_en"},
            {"name": "Reference", "get": "default_code"},
            {"name": "Code_national", "get": "cnk_code"},
            {"name": "TVA", "get": "vat"},
            {"name": "Prix_Vente_Indicatif", "get": lambda r: r.indicated_price or 0},
            {"name": "ean_13", "get": "barcode"},
            {"name": "ext_cti", "get": "code_cti"},
            {"name": "Prix_Brut_HTVA_EUR", "get": "gross_price"},
            {"name": "Prix_Brut_TVAC_EUR", "get": "gross_price_with_vat"},
            {"name": "Article_NL", "get": "name_nl"},
            {"name": "Category_NL", "get": "categ_nl"},
            {"name": "Mot_Cle", "get": "categ_fr"},
            {"name": "Article", "get": "name_fr"},
            {"name": "Fabricant", "get": "manufacturer"},
        ]
        if include_amm in ["true", "1", "t", "y", "yes"]:
            parser.append({"name": "Code_amm", "get": "code_amm"})
        return parser

    def _json_for_product_flattened_data(
        self, lang, data, include_amm=False, by_id=False
    ):
        parser = self._data_parser(include_amm=include_amm)
        values = {}
        for field_parser in parser:
            get = field_parser["get"]
            value = (getattr(data, get) if isinstance(get, str) else get(data)) or ""
            values[field_parser["name"]] = value
        if lang == "fr_BE":
            url_suffix = data.url_key_fr
        elif lang == "nl_BE":
            url_suffix = data.url_key_nl
        else:
            url_suffix = data.url_key_en
        lang_slug = LANGS_INVERSE[lang]
        url = f"https://www.alcyonbelux.be/{lang_slug}/{url_suffix}"
        values["url"] = url

        if self.partner.supplier_promotion_sale_allowed:
            promotions = []
            if data.supplier_discount_discount_sale and (
                not data.supplier_discount_only_for_veterinaries
                or self.partner.partner_type == "veterinary"
            ):
                discount = {
                    "promotion": data.supplier_discount_discount_sale,
                    "promotion_valid_until": data.supplier_discount_date_end,
                }
                promotions.append(discount)
            if data.has_supplier_promotion and (
                not data.supplier_promotion_only_for_veterinaries
                or self.partner.partner_type == "veterinary"
            ):
                promotion = {
                    "promotion": "FREE products",
                    "promotion_valid_until": data.supplier_promotion_date_end,
                }
                promotions.append(promotion)
            values["promotions"] = promotions
        return (data.id, values) if by_id else values


class FacadeCatalog(FacadeProduct):
    usage = "catalog"

    def process_kwargs(self, **kwargs):
        kwargs["lang"] = LANGS[kwargs.pop("language").lower()]
        return kwargs

    def apply(self, **kwargs):
        return self.env["alc.product.flattened.data"]._get_partner_products_iterator(
            self.partner
        )

    def process_result(self, result, **kwargs):
        lang = kwargs.pop("lang")
        include_amm = kwargs.pop("include_amm", "0") in ["true", "1", "t", "y", "yes"]
        f = self._json_for_product_flattened_data
        values = (f(lang, r, include_amm) for r in result)
        return self._json_to_xml(values, custom_root="catalog")


class FacadePriceList(FacadeProduct):
    usage = "sale_statistics"

    def apply(self, **kwargs):
        return (
            self.env["alc.eshop.sale_statistics_router.helper"]
            .new({"partner": self.partner})
            ._get_top_ordered()
        )

    def process_result(self, result, **kwargs):
        ids = [r["product_id"] for r in result["data"]]
        if not ids:
            self.errors = "<error>No bought product has been found</error>"
            return None
        records_data_iterator = self.env[
            "alc.product.flattened.data"
        ]._get_partner_products_iterator(self.partner, product_ids=ids)
        f = self._json_for_product_flattened_data
        values = [f("en_US", r, by_id=True) for r in records_data_iterator]
        json_by_id = {v[0]: v[1] for v in values}
        # we need to keep the order given by top_ordered
        data = (json_by_id[rid] for rid in ids if rid in json_by_id)
        return self._json_to_xml(data, custom_root="price_list")


class FacadeBackorders(Facade):
    usage = "pickings"

    def process_kwargs(self, **kwargs):
        from_date = kwargs.pop("date_cancelled", None)
        if not from_date:
            # takes the last 30 days
            from_date = datetime.date.today() - relativedelta(months=1)
        kwargs["from_date"] = from_date
        return kwargs

    def apply(self, **kwargs):
        from_date = kwargs.pop("from_date")
        if from_date:
            from_date = fields.Datetime.to_datetime(from_date)
        _total, records = search_pickings(
            self.env,
            partner=self.partner,
            states=["cancel"],
            from_date=from_date,
            canceled=True,
            include_total_count=False,
        )
        return records

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
            "date:date_cancelled",
            ("move_ids:items", parser_move_lines),
        ]


class FacadePackingSlip(Facade):
    usage = "pickings"

    def process_kwargs(self, **kwargs):
        from_date = kwargs.pop("date", None)
        if not from_date:
            # takes the last 30 days
            from_date = datetime.date.today() - relativedelta(months=1)
        kwargs["from_date"] = from_date
        return kwargs

    def apply(self, **kwargs):
        from_date = kwargs.pop("from_date")
        if from_date:
            from_date = fields.Datetime.to_datetime(from_date)
        _total, records = search_pickings(
            self.env,
            partner=self.partner,
            from_date=from_date,
            states=["done"],
            include_total_count=False,
        )
        return records

    @staticmethod
    def _item_func(parent):
        return "note" if parent == "packing_slip" else "item"

    def _json_for_xml(self, data):
        partner_dict = data.pop("partner_id")
        if not partner_dict:
            _logger.exception("Magento API packing data: %s", data)
        country_dict = partner_dict.pop("country_id", {}) or {}
        partner_dict["country"] = country_dict.get("name", "Belgique")
        data.update(partner_dict)
        items = []
        for item in data.pop("items"):
            if item.get("state") == "cancel":
                continue
            if not item.get("move_id"):
                # a move_line without move_id is a move_line that has been
                # cancelled or is not done... we should not have it
                continue
            item.pop("state", None)
            item.update(item.pop("product_id"))
            item.update(item.pop("move_id"))
            lot = item.pop("lot_id")
            if lot:  # we should not need to drop other lots in future versions
                item.update(lot)
            else:
                item["lot"] = None
            if item.get("peremption"):
                item["peremption"] = self._datetime_to_date(item["peremption"])
            else:
                item["peremption"] = None
            # TVA is from vat, which is a related to the name (e.g. 21%)
            tva = item["tva"]
            item["tva"] = tva[:-1] if isinstance(tva, str) else tva
            items.append(item)
        data["items"] = items
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
        parser_lot = ["name:lot", "expiration_date:peremption"]
        parser_move_line_ids = [
            "state",
            "qty_done:qty",
            ("product_id", parser_product),
            ("lot_id", parser_lot),
            (
                "move_id",
                [
                    "description_picking:name",
                    "suite_name:numero_de_suite",
                    ("prix_net_htva", self._get_price_from_move),
                    ("prix_brut_htva", self._get_price_from_move),
                ],
            ),
        ]
        return [
            "id:ne_id",
            "date_done:date",
            ("partner_id", parser_partner),
            ("move_line_ids:items", parser_move_line_ids),
        ]

    def _get_price_from_move(self, stock_move, field_name):
        if field_name == "prix_net_htva":
            return stock_move.sale_line_id.price_reduce_taxexcl
        if field_name == "prix_brut_htva":
            return stock_move.sale_line_id.price_unit
        return 0.0


class FacadeShopinvaderCart(Facade):
    usage = "cart"
    collection = "shopinvader.api.v2"

    def apply(self, **kwargs):
        info = kwargs.pop("info", None)
        if info:
            cart = self.cart_router_helper._update_cart_info(None, info)
        else:
            cart = self.cart_router_helper._find_open_cart(self.partner.id, None)
        sync = kwargs.pop("sync", None)
        if sync:
            self.cart_router_helper._sync_cart(
                partner=self.partner,
                cart=cart,
                uuid=None,
                transactions=sync.transactions,
            )

    def _get_product_by_sku(self, sku):
        domain = self.env["product.product"].get_partner_type_domain(self.partner)
        domain.append(("default_code", "=", sku))
        return self.env["product.product"].search(domain, limit=1)

    def __init__(self, env, partner):
        super().__init__(env, partner)
        self.cart_router_helper = self.env[
            "shopinvader_api_cart.cart_router.helper"
        ].new({"partner": partner})
        location_param = "alc_magento_api.cart_location"
        self.location = self.env["ir.config_parameter"].sudo().get_param(location_param)

    def process_errors(self, result, **kwargs):
        error = None
        if len(self.errors) == 1:
            error = f"<error>The product {self.errors[0]} is not available</error>"
        elif len(self.errors) > 1:
            missing = ", ".join(self.errors)
            error = f"<error>The products {missing} are not available</error>"
        return error


class FacadeQuote(FacadeShopinvaderCart):
    def process_kwargs(self, **kwargs):
        quote_xml = kwargs.pop("data")
        quote_dict = self._xml_to_json(quote_xml)["quote"]

        transactions: list[CartTransaction] = []
        items = quote_dict.pop("item", [])
        items = [items] if isinstance(items, dict) else items
        for line_xml in items:
            product = self._get_product_by_sku(line_xml["sku"])
            if product:
                qty = int(line_xml["qty"])
                line_id = str(uuid.uuid4())
                transactions.append(
                    CartTransaction(
                        product_id=product.id,
                        qty=qty,
                        uuid=line_id,
                    )
                )
            else:
                self.errors.append(line_xml["sku"])
        kwargs["sync"] = CartSyncInput(transactions=transactions)

        kwargs["info"] = CartUpdateRequest(
            note=quote_dict.get("comments"),
            suite_name=quote_dict.get("serial_number"),
            customer_ref=quote_dict.get("order_reference"),
        )
        return kwargs


class FacadeQuoteCsv(FacadeShopinvaderCart):
    def apply(self, **kwargs):
        csv_file = kwargs.pop("file")
        not_found_skus, _cart = self.cart_router_helper._import_csv(csv_file)
        self.errors.extend(not_found_skus)
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
        domain = [("partner_id", "=", self.partner.id), ("typology", "=", "sale")]
        from_date = kwargs.pop("from_date")
        if from_date:
            from_date = fields.Datetime.to_datetime(from_date)
            from_date = from_date.astimezone(pytz.timezone("UTC"))
            domain.append(("create_date", ">=", from_date))
        domain.append(
            (
                "sale_channel_id",
                "in",
                self.env["sale.channel"].sudo()._get_internal_ids(),
            )
        )
        return self.env["sale.order"].sudo().search(domain)

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
