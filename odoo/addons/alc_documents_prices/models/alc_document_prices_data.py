# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

import odoo.addons.decimal_precision as dp


class AlcDocumentPriceData(models.Model):

    _name = "alc.document.prices.data"
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
    price_cache = fields.Serialized(readonly=True)
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

    @api.model
    def get_init_query(self):
        return """
            CREATE MATERIALIZED VIEW %(table)s AS (
WITH web_categories AS (
    SELECT
        *,
        row_number() OVER (PARTITION BY product_id ORDER BY categ_id DESC) as idx
    FROM product_categ_rel
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
    indicated_price,
    pp.barcode,
    categ.name as categ_en,
    coalesce(categ_fr.value, categ.name) as categ_fr,
    coalesce(categ_nl.value, categ.name) as categ_nl,
    pp.allowed_partner_types,
    price_cache,
    supplier_promotion.id is not null as has_supplier_promotion,
    supplier_promotion.date_end as supplier_promotion_date_end,
    supplier_discount.discount_sale as supplier_discount_discount_sale,
    supplier_discount.date_end as supplier_discount_date_end,
    discount_special.id is not null as has_discount_special,
    discount_special.date_end as discount_special_date_end,
    tax.amount as tax_amount,
    supplier.name as supplier_name,
    web_published

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
    LEFT join product_category categ
        on categ.id = web_categs.categ_id
    LEFT join ir_translation as categ_fr
        ON categ_fr.res_id = categ.id
        AND categ_fr.type = 'model'
        AND categ_fr.name = 'product.category,name'
        AND categ_fr.lang = 'fr_BE'
    LEFT join ir_translation as categ_nl
        ON categ_nl.res_id = categ.id
        AND categ_nl.type = 'model'
        AND categ_nl.name = 'product.category,name'
        AND categ_nl.lang = 'nl_BE'
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
    LEFT join product_taxes_rel as taxes_rel
            ON taxes_rel.prod_id = pt.id
    LEFT join account_tax as tax
        ON taxes_rel.tax_id = tax.id
        and tax.tax_group_id = %(tax_group_one_tax_id)s
    LEFT join res_partner as supplier
        ON supplier.id = pt.supplier_id
WHERE pt.active and web_published

);

CREATE UNIQUE INDEX pk_%(table)s ON %(table)s (id);

"""

    @api.model
    def get_init_query_args(self):
        args = super(AlcDocumentPriceData, self).get_init_query_args()
        args["tax_group_one_tax_id"] = self.env.ref(
            "account_tax_one_vat.vat_tax_group"
        ).id
        return args
