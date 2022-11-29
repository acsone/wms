# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import ujson
from psycopg2.extensions import AsIs

from odoo import api, fields, models
from odoo.osv import expression
from odoo.osv.query import Query

import odoo.addons.decimal_precision as dp
from odoo.addons.alc_pg_trgm.utils import install_trgm_extension


class AlcProductFlattenedData(models.Model):

    _name = "alc.product.flattened.data"
    _inherit = "materialized.view.mixin"
    _description = "Product informations for document prices"
    _auto = False

    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    product_tmpl_id = fields.Many2one(comodel_name="product.template", readonly=True)
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
        string="Indicated price",
        digits=dp.get_precision("Product Price"),
        readonly=True,
    )
    barcode = fields.Char(readonly=True)
    categ_en = fields.Char(readonly=True)
    categ_fr = fields.Char(readonly=True)
    categ_nl = fields.Char(readonly=True)
    allowed_partner_types = fields.Char(readonly=True)
    price_cache = fields.Serialized(readonly=True, prefetch=True)
    supplier_discount_discount_sale = fields.Float(
        "Sale discount (%)",
        digits=dp.get_precision("Discount"),
        default=0.0,
        readonly=True,
    )
    supplier_discount_date_end = fields.Date(readonly=True)
    has_supplier_promotion = fields.Boolean(readonly=True)
    supplier_promotion_date_end = fields.Date(readonly=True)
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
        product_category.name as fullname_en,
        coalesce(categ_fr.value, product_category.name) as fullname_fr,
        coalesce(categ_nl.value, product_category.name) as fullname_nl
    FROM product_category
        LEFT join ir_translation as categ_fr
            ON categ_fr.res_id = product_category.id
            AND categ_fr.type = 'model'
            AND categ_fr.name = 'product.category,name'
            AND categ_fr.lang = 'fr_BE'
        LEFT join ir_translation as categ_nl
            ON categ_nl.res_id = product_category.id
            AND categ_nl.type = 'model'
            AND categ_nl.name = 'product.category,name'
            AND categ_nl.lang = 'nl_BE'
    WHERE product_category.parent_id = %(main_web_category_id)s
    UNION
        SELECT
            product_category.id,
            product_category.parent_id,
            product_category.name,
            cs.fullname_en || ' / ' || product_category.name as fullname_en,
            cs.fullname_fr || ' / ' || coalesce(categ_fr.value, product_category.name) as fullname_fr,
            cs.fullname_nl || ' / ' || coalesce(categ_nl.value, product_category.name) as fullname_nl
        FROM
            categ_info cs
        JOIN
            product_category on cs.id = product_category.parent_id
            LEFT join ir_translation as categ_fr
                ON categ_fr.res_id = product_category.id
                AND categ_fr.type = 'model'
                AND categ_fr.name = 'product.category,name'
                AND categ_fr.lang = 'fr_BE'
            LEFT join ir_translation as categ_nl
                ON categ_nl.res_id = product_category.id
                AND categ_nl.type = 'model'
                AND categ_nl.name = 'product.category,name'
                AND categ_nl.lang = 'nl_BE'
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
            AND tax.tax_group_id = %(tax_group_one_tax_id)s
)
SELECT
    pp.id,
    pt.id as product_tmpl_id,
    pp.id as product_id,
    pt.default_code,
    pt.name as name_en,
    coalesce(name_fr.value, pt.name) as name_fr,
    coalesce(name_nl.value, pt.name) as name_nl,
    coalesce(name_de.value, pt.name) as name_de,
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
    supplier_discount.discount_sale as supplier_discount_discount_sale,
    supplier_discount.date_end as supplier_discount_date_end,
    discount_special.id is not null as has_discount_special,
    discount_special.date_end as discount_special_date_end,
    tax.amount as tax_amount,
    supplier.name as supplier_name,
    web_published,
    url_key_fr.url_key as url_key_fr,
    url_key_nl.url_key as url_key_nl,
    url_key_en.url_key as url_key_en
FROM
    product_template pt
    join product_product pp on pp.product_tmpl_id = pt.id
    LEFT join ir_translation as name_fr
        ON name_fr.res_id = pt.id
        AND name_fr.type = 'model'
        AND name_fr.name = 'product.template,name'
        AND name_fr.lang = 'fr_BE'
    LEFT join ir_translation as name_nl
        ON name_nl.res_id = pt.id
        AND name_nl.type = 'model'
        AND name_nl.name = 'product.template,name'
        AND name_nl.lang = 'nl_BE'
    LEFT join ir_translation as name_de
        ON name_de.res_id = pt.id
        AND name_de.type = 'model'
        AND name_de.name = 'product.template,name'
        AND name_de.lang = 'de_DE'
    LEFT join res_partner as manufacturer
        on pt.manufacturer = manufacturer.id
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
            url_key
        FROM shopinvader_product sp
        JOIN res_lang
            ON res_lang.id = sp.lang_id
        WHERE
            record_id = pt.id
            AND res_lang.code = 'fr_BE'
        limit 1
    ) as url_key_fr ON TRUE
    LEFT JOIN LATERAL (
        SELECT
            url_key
        FROM shopinvader_product sp
        JOIN res_lang
            ON res_lang.id = sp.lang_id
        WHERE
            record_id = pt.id
            AND res_lang.code = 'nl_BE'
        limit 1
    ) as url_key_nl ON TRUE
    LEFT JOIN LATERAL (
        SELECT
            url_key
        FROM shopinvader_product sp
        JOIN res_lang
            ON res_lang.id = sp.lang_id
        WHERE
            record_id = pt.id
            AND res_lang.code = 'en_US'
        limit 1
    ) as url_key_en ON TRUE

WHERE pp.active and web_published

);

CREATE UNIQUE INDEX pk_%(table)s ON %(table)s (id);

"""

    @api.model
    def get_init_query_args(self):
        args = super(AlcProductFlattenedData, self).get_init_query_args()
        args["tax_group_one_tax_id"] = self.env.ref(
            "account_tax_one_vat.vat_tax_group"
        ).id
        args["main_web_category_id"] = self.env.ref(
            "alc_product_shop_category.master"
        ).id
        return args

    @api.model_cr
    def init(self):
        res = super(AlcProductFlattenedData, self).init()
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
        """Generator method to get one by one line as a simple object where
        each column is accessed with a doc notation"""
        e = expression.expression(domain, self)
        tables = e.get_tables()
        where_clause, where_params = e.to_sql()
        where_clause = [where_clause] if where_clause else []
        query = Query(tables, where_clause, where_params)
        query_from, query_where, query_params = query.get_sql()
        # pylint: disable=sql-injection
        sql_query = "SELECT * from {query_from} WHERE {query_where}".format(
            query_from=query_from, query_where=query_where
        )
        if limit:
            query_params.append(limit)
            sql_query += " limit %s"
        if offset:
            query_params.append(offset)
            sql_query += " offset %s"
        # avoid name conflict; note that the problem might still occur if we try
        # to get two iterators in the same transaction...
        name = "iterator %s" % self.env.cr
        named_cursor = self.env.cr._obj.connection.cursor(name)
        named_cursor.execute(sql_query, query_params)
        try:
            for row in named_cursor:
                container = _ProductDataContainer(
                    self.env,
                    partner,
                    **{d.name: row[i] for i, d in enumerate(named_cursor.description)}
                )
                yield container
        finally:
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
            if isinstance(elem, (unicode, str)):
                new_domain.append(elem)
            else:  # we have a triple
                x, y, z = elem
                if x in ["url_key", "name", "categ"]:
                    x = "_".join((x, suffix))
                new_domain.append((x, y, z))
        return new_domain


class _Container(object):
    """
        A generic container for when you want to access to value into a dict
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
        super(_ProductDataContainer, self).__init__(**kwargs)
        # here we use ujson to improve to increase perf X 5
        self.price_cache = ujson.loads(self.price_cache) if self.price_cache else {}
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
