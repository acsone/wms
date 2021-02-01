# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

import odoo.addons.decimal_precision as dp


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"
    _order = "is_null_date_start, date_start DESC, min_qty DESC, min_qty_sale DESC"

    is_null_date_start = fields.Boolean(
        "The date start is null",
        compute="_compute_is_null_date_start",
        store=True,
        readonly=True,
    )
    discount_purchase = fields.Float(
        "Purchase discount (%)", digits=dp.get_precision("Discount"), default=0.0
    )

    discount_sale = fields.Float(
        "Sale discount (%)", digits=dp.get_precision("Discount"), default=0.0
    )

    min_qty_sale = fields.Float(string="Sale minimum qty", default=0.0)

    min_qty = fields.Float(string="Purchase minimum qty")

    @api.model
    def _get_default_line(self, supplier_partner_id, product_tmpl_id):
        if not supplier_partner_id or not product_tmpl_id:
            return self.browse()
        return self.search(
            [
                ("name", "=", supplier_partner_id),
                ("product_tmpl_id", "=", product_tmpl_id),
                ("date_start", "=", False),
                ("date_end", "=", False),
            ],
            limit=1,
        )

    @api.onchange("name", "product_tmpl_id")
    def compute_default_price(self):
        for promo in self:
            if promo.price or (not promo.name or not promo.product_tmpl_id):
                continue

            # When open the wizard to create a new promotion, the value
            # for product_tmpl_id is a temporary id (NewID).
            product_tmpl_id = promo.product_tmpl_id.id
            if not product_tmpl_id:
                product_tmpl_id = self._context.get("default_product_tmpl_id")

            default_line = self._get_default_line(promo.name.id, product_tmpl_id)
            if not default_line:
                continue

            promo.price = default_line.price

    @api.depends("date_start")
    def _compute_is_null_date_start(self):
        """
        By default we cannot order DESC and put all nulls at the end with Odoo
        (ORDER BY date_start DESC NULLS LAST)
        Change the code of Odoo to allows ordering nulls last is really touchy.
        To avoid that I create a simply boolean to say if the field date_start
        is null and I order on this field.
        """
        for promo in self:
            promo.is_null_date_start = bool(not promo.date_start)

    @api.constrains("date_start", "date_end", "name", "min_qty", "min_qty_sale")
    def check_dates(self):
        # Used by imports to avoid problems with imported data
        if self._context.get("disable_check_dates"):
            return

        for promo in self:
            other_supplier = self.search(
                [
                    ("product_tmpl_id", "=", promo.product_tmpl_id.id),
                    ("name", "!=", promo.name.id),
                ]
            )
            if other_supplier:
                raise ValidationError(
                    _("You cannot two different supplier for a product")
                )

            if not promo.date_start and not promo.date_end:
                if promo.min_qty > 1 or promo.min_qty_sale > 1:
                    raise ValidationError(
                        _(
                            "You cannot set a minimum quantity (sale and/or "
                            "purchase) on a default promo"
                        )
                    )

                existing_open_promo = self.search(
                    [
                        ("product_tmpl_id", "=", promo.product_tmpl_id.id),
                        ("date_start", "=", False),
                        ("date_end", "=", False),
                        ("id", "!=", promo.id),
                    ]
                )
                if existing_open_promo:
                    raise ValidationError(
                        _("You cannot have two promos " "without start and end date")
                    )
            elif not promo.date_start and promo.date_end:
                raise ValidationError(_("You cannot have a promo without start date"))
            elif promo.date_start and not promo.date_end:
                raise ValidationError(_("You cannot have a promo without end date"))
            else:
                if promo.date_start > promo.date_end:
                    raise ValidationError(
                        _(
                            "The end date must be equal "
                            "or greater than the start date"
                        )
                    )

                existing_promos = self.search(
                    [
                        ("product_tmpl_id", "=", promo.product_tmpl_id.id),
                        ("date_end", ">=", promo.date_start),
                        ("date_start", "<=", promo.date_end),
                        ("min_qty", "=", promo.min_qty),
                        ("min_qty_sale", "=", promo.min_qty_sale),
                        ("id", "!=", promo.id),
                    ]
                )
                if existing_promos:
                    raise ValidationError(
                        _("You cannot have two promos at the same time")
                    )

    @api.model
    def create(self, vals):
        # when the record is created by import, the price is not always given...
        # if not takes the default one
        if not vals.get("price"):
            vals["price"] = self._get_default_line(
                vals["name"], vals["product_tmpl_id"]
            ).price
        return super(ProductSupplierinfo, self).create(vals)
