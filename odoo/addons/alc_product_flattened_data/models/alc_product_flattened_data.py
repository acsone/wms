# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

import orjson
from psycopg2.extensions import AsIs

from odoo import api, fields
from odoo.models import Model
from odoo.osv import expression

from odoo.addons.alc_pg_trgm.utils import install_trgm_extension
from odoo.addons.base_sparse_field.models.fields import Serialized
from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.product.models.product_template import ProductTemplate

_logger = logging.getLogger(__name__)


class AlcProductFlattenedData(Model):

    _name = "alc.product.flattened.data"
    _inherit = "materialized.view.mixin"
    _description = "Product informations for document prices"
    _auto = False

    product_id = fields.Many2one[ProductProduct](readonly=True)
    product_tmpl_id = fields.Many2one[ProductTemplate](readonly=True)
    default_code = fields.Char(readonly=True)
    name_en = fields.Char(readonly=True)
    name_fr = fields.Char(readonly=True)
    name_nl = fields.Char(readonly=True)
    name_de = fields.Char(readonly=True)
    manufacturer = fields.Char(readonly=True)
    cnk_code = fields.Char(readonly=True)
    code_amm = fields.Char(readonly=True)
    code_cti = fields.Char(readonly=True)
    indicated_price = fields.Float(
        string="Indicated price", digits="Product Price", readonly=True
    )
    barcode = fields.Char(readonly=True)
    categ_en = fields.Char(readonly=True)
    categ_fr = fields.Char(readonly=True)
    categ_nl = fields.Char(readonly=True)
    allowed_partner_types = fields.Char(readonly=True)
    price_cache = Serialized(readonly=True, prefetch=True)
    supplier_discount_discount_sale = fields.Float(
        "Sale discount (%)", digits="Discount", default=0.0, readonly=True
    )
    supplier_discount_only_for_veterinaries = fields.Boolean(readonly=True)
    supplier_discount_date_end = fields.Date(readonly=True)
    has_supplier_promotion = fields.Boolean(readonly=True)
    supplier_promotion_date_end = fields.Date(readonly=True)
    supplier_promotion_only_for_veterinaries = fields.Boolean(readonly=True)
    has_discount_special = fields.Boolean(readonly=True)
    discount_special_date_end = fields.Date(readonly=True)
    web_published = fields.Boolean(readonly=True)
    supplier_name = fields.Char(readonly=True)
    tax_amount = fields.Float(readonly=True, digits=(16, 4))
    url_key_fr = fields.Char(readonly=True)
    url_key_en = fields.Char(readonly=True)
    url_key_nl = fields.Char(readonly=True)

    @api.model
    def get_init_query(self):
        return """
            CREATE MATERIALIZED VIEW %(table)s AS (
WITH RECURSIVE categ_info AS (
    SELECT
        product_category.id,
        parent_id,
        product_category.name,
        product_category.name->>'en_US' as fullname_en,
        coalesce(product_category.name->>'fr_BE', product_category.name->>'en_US') as fullname_fr,
        coalesce(product_category.name->>'nl_BE', product_category.name->>'en_US') as fullname_nl
    FROM product_category
    WHERE product_category.parent_id = %(main_web_category_id)s
    UNION
        SELECT
            product_category.id,
            product_category.parent_id,
            product_category.name,
            concat(cs.fullname_en, ' / ', product_category.name->>'en_US') as fullname_en,
            concat(cs.fullname_fr, ' / ', coalesce(product_category.name->>'fr_BE', product_category.name->>'en_US')) as fullname_fr,
            concat(cs.fullname_nl, ' / ', coalesce(product_category.name->>'nl_BE', product_category.name->>'en_US')) as fullname_nl
        FROM
            categ_info cs
        JOIN
            product_category on cs.id = product_category.parent_id

),
web_categories AS (
    SELECT
        *,
        row_number() OVER (PARTITION BY product_id ORDER BY categ_id DESC) as idx
    FROM product_categ_rel
),
single_tax AS (
    SELECT
        prod_id,
        tax.*
    FROM
        product_taxes_rel trel
        JOIN account_tax tax
            ON trel.tax_id = tax.id
            AND tax.is_vat
)
SELECT
    pp.id,
    pt.id as product_tmpl_id,
    pp.id as product_id,
    pt.default_code,
    pt.name->>'en_US' as name_en,
    coalesce(pt.name->>'fr_BE', pt.name->>'en_US') as name_fr,
    coalesce(pt.name->>'nl_BE', pt.name->>'en_US') as name_nl,
    coalesce(pt.name->>'de_DE', pt.name->>'en_US') as name_de,
    manufacturer.name as manufacturer,
    cnk_code,
    code_amm,
    code_cti,
    indicated_price,
    pp.barcode,
    categ.fullname_en as categ_en,
    categ.fullname_fr as categ_fr,
    categ.fullname_nl as categ_nl,
    pt.allowed_partner_types,
    price_cache,
    supplier_promotion.id is not null as has_supplier_promotion,
    supplier_promotion.date_end as supplier_promotion_date_end,
    supplier_promotion.only_for_veterinaries as supplier_promotion_only_for_veterinaries,
    supplier_discount.discount_sale as supplier_discount_discount_sale,
    supplier_discount.date_end as supplier_discount_date_end,
    supplier_promotion.only_for_veterinaries as supplier_discount_only_for_veterinaries,
    discount_special.id is not null as has_discount_special,
    discount_special.date_end as discount_special_date_end,
    tax.amount as tax_amount,
    supplier.name as supplier_name,
    web_published,
    url_key_fr.key as url_key_fr,
    url_key_nl.key as url_key_nl,
    url_key_en.key as url_key_en
FROM
    product_template pt
    join product_product pp on pp.product_tmpl_id = pt.id
    LEFT join res_partner as manufacturer
        on pt.manufacturer_id = manufacturer.id
    LEFT join web_categories web_categs
        on web_categs.product_id = pt.id
        AND web_categs.idx = 1
    LEFT join categ_info categ
        on categ.id = web_categs.categ_id
    LEFT join product_supplierinfo as supplier_discount
        ON supplier_discount.product_tmpl_id = pt.id
        AND supplier_discount.date_start <= CURRENT_DATE AND supplier_discount.date_end >= CURRENT_DATE
        AND supplier_discount.discount_sale > 0
    LEFT join product_supplierinfo as supplier_promotion
        ON supplier_promotion.product_tmpl_id = pt.id
        AND supplier_promotion.date_start <= CURRENT_DATE AND supplier_promotion.date_end >= CURRENT_DATE
        AND supplier_promotion.ratio_main_product > 0
        AND supplier_promotion.ratio_promotional_product > 0
    LEFT join product_discount_special as discount_special
        ON discount_special.product_template_id = pt.id
        AND discount_special.date_start <= CURRENT_DATE AND discount_special.date_end >= CURRENT_DATE
    LEFT join single_tax as tax
        ON tax.prod_id = pt.id
    LEFT join res_partner as supplier
        ON supplier.id = pt.supplier_id
    LEFT JOIN LATERAL (
        SELECT
            key
        FROM url_url
        JOIN res_lang
            ON res_lang.id = url_url.lang_id
        WHERE
            res_id = pt.id
            AND res_lang.code = 'fr_BE'
            AND res_model = 'product.template'
            AND redirect = False
        limit 1
    ) as url_key_fr ON TRUE
    LEFT JOIN LATERAL (
        SELECT
            key
        FROM url_url
        JOIN res_lang
            ON res_lang.id = url_url.lang_id
        WHERE
            res_id = pt.id
            AND res_lang.code = 'n_BE'
            AND res_model = 'product.template'
            AND redirect = False
        limit 1
    ) as url_key_nl ON TRUE
    LEFT JOIN LATERAL (
        SELECT
            key
        FROM url_url
        JOIN res_lang
            ON res_lang.id = url_url.lang_id
        WHERE
            res_id = pt.id
            AND res_lang.code = 'en_US'
            AND res_model = 'product.template'
            AND redirect = False
        limit 1
    ) as url_key_en ON TRUE

WHERE pp.active and web_published

);

CREATE UNIQUE INDEX pk_%(table)s ON %(table)s (id);

"""

    @api.model
    def get_init_query_args(self):
        args = super().get_init_query_args()
        args["main_web_category_id"] = self.env.ref(
            "alc_product_shop_category.master"
        ).id
        return args

    def init(self):
        res = super().init()
        trgm_installed = install_trgm_extension(self.env)
        if trgm_installed:
            index_name = "alc_product_flatted_data_partner_types_index"
            self.env.cr.execute(
                "SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,)
            )
            if not self.env.cr.fetchone():
                self.env.cr.execute(
                    "CREATE INDEX %s ON %s USING GIN (allowed_partner_types gin_trgm_ops)",
                    (AsIs(index_name), AsIs(self._table)),
                )
        return res

    @api.model
    def _get_iterator(self, domain, partner=None, limit=None, offset=None):
        """Generator method to get one by one line as a simple object where.

        each column is accessed with a doc notation
        """
        e = expression.expression(domain, self)
        query = e.query
        query_from, query_where, query_params = query.get_sql()
        # we don't want to receive the json as dict but as string
        # we instruct psycopg2 to do so
        cols = ", ".join([f.name for f in self._fields.values() if f.store])
        cols = cols.replace("price_cache", "price_cache::text")
        sql_query = f"SELECT {cols} from {query_from} WHERE {query_where}"
        if limit:
            query_params.append(limit)
            sql_query += " limit %s"
        if offset:
            query_params.append(offset)
            sql_query += " offset %s"
        # avoid name conflict; note that the problem might still occur if we try
        # to get two iterators in the same transaction...
        name = f"iterator {self.env.cr}"
        named_cursor = self.env.cr._obj.connection.cursor(name)
        named_cursor.execute(sql_query, query_params)
        for row in named_cursor:
            container = _ProductDataContainer(
                self.env,
                partner,
                **{d.name: row[i] for i, d in enumerate(named_cursor.description)},
            )
            yield container
        named_cursor.close()

    @api.model
    def _get_partner_products_iterator(
        self, partner, product_ids=None, domain_extend=None, limit=None, offset=None
    ):
        domain_product = partner._get_product_domain()
        if domain_extend:
            domain_product = expression.AND([domain_product, domain_extend])
        if product_ids:
            domain_product = expression.AND(
                [domain_product, [("id", "in", product_ids)]]
            )
        return self._get_iterator(domain_product, partner, limit, offset)

    @api.model
    def _product_domain_to_model_domain(self, domain):
        # we could also convert id to product_id
        new_domain = []
        suffix = "en"
        lang = self.env.lang or ""
        for prefix in ("fr", "nl"):
            if prefix in lang:
                suffix = prefix
        for elem in domain:
            if isinstance(elem, str):
                new_domain.append(elem)
            else:  # we have a triple
                x, y, z = elem
                if x in ["url_key", "name", "categ"]:
                    x = "_".join((x, suffix))
                new_domain.append((x, y, z))
        return new_domain


class _Container:
    """
    A generic container for when you want to access to value into a dict.

    with a dot notation
    ex:
    >>> c = _Container(**{"a": "b"})
    >>> c.a
    "b"
    """

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class _ProductDataContainer(_Container):
    def __init__(self, env, partner, **kwargs):
        self._env = env
        self._partner = partner
        super().__init__(**kwargs)
        self.price_cache = orjson.loads(self.price_cache) if self.price_cache else {}
        # init and compute prices
        # init and compute prices
        self.gross_price = 0
        self.gross_price_with_vat = 0
        self._resolve_prices()

    def _resolve_prices(self):
        partner = self._partner
        if not partner:
            return
        price_key = partner.property_product_pricelist.role_name
        self.gross_price = (
            self._env["product.product"]
            ._resolve_price_cache_get(self.price_cache, price_key)
            .get("price", 0)
        )
        self.gross_price_with_vat = round(
            self.gross_price + self.gross_price * self.vat / 100, 2
        )

    @property
    def vat(self):
        return self.tax_amount or 21

    @property
    def name(self):
        lang = self._env.lang or ""
        if "fr" in lang:
            return self.name_fr
        if "nl" in lang:
            return self.name_nl
        return self.name_en

    @property
    def url_key(self):
        lang = self._env.lang or ""
        if "fr" in lang:
            return self.url_key_fr
        if "nl" in lang:
            return self.url_key_nl
        return self.url_key_en

    @property
    def categ(self):
        lang = self._env.lang or ""
        if "fr" in lang:
            return self.categ_fr
        if "nl" in lang:
            return self.categ_nl
        return self.categ_en
