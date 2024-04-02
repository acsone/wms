# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields

from odoo.addons.mixin_past.models.mixin_past import MixinPast
from odoo.addons.product.models.product_supplierinfo import SupplierInfo


class ProductSupplierInfo(SupplierInfo, MixinPast):
    _name = "product.supplierinfo"
    _order = "is_null_date_start, date_start DESC, min_qty DESC, min_qty_sale DESC"

    is_null_date_start = fields.Boolean(
        "The date start is null",
        compute="_compute_is_null_date_start",
        store=True,
        readonly=True,
    )

    is_promotion = fields.Boolean(compute="_compute_promotions", store=False)
    is_sale_discount = fields.Boolean(compute="_compute_promotions", store=False)
    ratio_main_product = fields.Integer("Ratio Main Product")
    ratio_promotional_product = fields.Integer("Ratio Free Product")
    ratio_display_name = fields.Char(
        "Promotion", compute="_compute_ratio_display_name", readonly=True
    )
    discount_sale = fields.Float("Sale discount (%)", digits="Discount", default=0.0)
    min_qty_sale = fields.Float(string="Sale minimum qty", default=0.0)
    min_qty = fields.Float(string="Purchase minimum qty")
    # IDEA could be a list of promotion scopes
    # a promotion scope could be based on partner_type or whatever scopes
    # emerging from the business needs
    only_for_veterinaries = fields.Boolean(
        "Only for veterinaries",
        default=False,
        help="This field only apply to buyx_gety promotion",
    )

    _sql_constraints = [
        (
            "valid_promotion_buyx_gety",
            """CHECK ((ratio_main_product > 0 and ratio_promotional_product > 0) or
               ((ratio_main_product is NULL or ratio_main_product = 0) and
                (ratio_promotional_product is NULL or
                 ratio_promotional_product = 0)))
            """,
            _(
                """A valid promotion on quantity must have both value higher than
                 zero"""
            ),
        )
    ]

    @api.depends("date_start")
    def _compute_is_null_date_start(self):
        """
        By default we cannot order DESC and put all nulls at the end with Odoo.

        (ORDER BY date_start DESC NULLS LAST)
        Change the code of Odoo to allows ordering nulls last is really touchy.
        To avoid that I create a simply boolean to say if the field date_start
        is null and I order on this field.
        """
        for promo in self:
            promo.is_null_date_start = bool(not promo.date_start)

    @api.depends("ratio_promotional_product", "ratio_main_product")
    def _compute_ratio_display_name(self):
        for rec in self:
            if not rec.ratio_promotional_product or not rec.ratio_main_product:
                rec.ratio_display_name = ""
                continue
            display_name = _(
                "For %(ratio_main_product)s products, %(ratio_promotional_product)s free",
                ratio_main_product=rec.ratio_main_product,
                ratio_promotional_product=rec.ratio_promotional_product,
            )
            rec.ratio_display_name = display_name

    @api.depends("discount_sale", "ratio_main_product", "ratio_promotional_product")
    def _compute_promotions(self):
        for record in self:
            record.is_sale_discount = bool(record.discount_sale)
            record.is_promotion = (
                record.ratio_main_product and record.ratio_promotional_product
            )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "default_product_tmpl_id" in self._context and self._context.get(
            "default_product_tmpl_id"
        ):
            product_template = self.env["product.template"].browse(
                self._context.get("default_product_tmpl_id")
            )
            defaults["partner_id"] = product_template.supplier_id.id
        return defaults
