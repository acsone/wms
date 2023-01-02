# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


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
        "Purchase discount (%)", digits="Discount", default=0.0
    )
    discount_sale = fields.Float("Sale discount (%)", digits="Discount", default=0.0)
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

    @api.onchange("partner_id", "product_tmpl_id")
    def _onchange_default_price(self):
        for rec in self:
            if rec.price or (not rec.name or not rec.product_tmpl_id):
                continue
            # When open the wizard to create a new promotion, the value
            # for product_tmpl_id is a temporary id (NewID).
            product_tmpl_id = rec.product_tmpl_id.id
            if not product_tmpl_id:
                product_tmpl_id = self._context.get("default_product_tmpl_id")
            default_line = self._get_default_line(rec.partner_id.id, product_tmpl_id)
            if default_line:
                rec.price = default_line.price

    @api.depends("date_start")
    def _compute_is_null_date_start(self):
        """
        By default we cannot order DESC and put all nulls at the end with Odoo.

        (ORDER BY date_start DESC NULLS LAST)
        Change the code of Odoo to allows ordering nulls last is really touchy.
        To avoid that I create a simply boolean to say if the field date_start
        is null and I order on this field.
        """
        for rec in self:
            rec.is_null_date_start = bool(not rec.date_start)

    def _check_unique_supplier(self):
        self.ensure_one()
        other_supplier = self.search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("name", "!=", self.name.id),
            ]
        )
        if other_supplier:
            raise ValidationError(_("You cannot two different supplier for a product"))

    def _check_min_qty(self):
        self.ensure_one()
        if self.min_qty > 1 or self.min_qty_sale > 1:
            raise ValidationError(
                _(
                    "You cannot set a minimum quantity (sale and/or "
                    "purchase) on a default promo"
                )
            )

    def _check_existing_open_promo(self):
        self.ensure_one()
        existing_open_promo = self.search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("date_start", "=", False),
                ("date_end", "=", False),
                ("id", "!=", self.id),
            ]
        )
        if existing_open_promo:
            raise ValidationError(
                _("You cannot have two promos " "without start and end date")
            )

    def _check_existing_promo(self):
        self.ensure_one()
        existing_promos = self.search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("date_end", ">=", self.date_start),
                ("date_start", "<=", self.date_end),
                ("min_qty", "=", self.min_qty),
                ("min_qty_sale", "=", self.min_qty_sale),
                ("id", "!=", self.id),
            ]
        )
        if existing_promos:
            raise ValidationError(_("You cannot have two promos at the same time"))

    def _check_date_start(self):
        self.ensure_one()
        if not self.date_start and self.date_end:
            raise ValidationError(_("You cannot have a promo without start date"))

    def _check_date_end(self):
        self.ensure_one()
        if self.date_start and not self.date_end:
            raise ValidationError(_("You cannot have a promo without end date"))

    def _check_dates(self):
        self.ensure_one()
        if self.date_start and self.date_end and self.date_start > self.date_end:
            raise ValidationError(
                _("The end date must be equal or greater than the start date")
            )

    @api.constrains("date_start", "date_end", "name", "min_qty", "min_qty_sale")
    def check_dates(self):
        # Used by imports to avoid problems with imported data
        if self._context.get("disable_check_dates"):
            return
        for rec in self:
            rec._check_unique_supplier()
            if not rec.date_start and not rec.date_end:
                self._check_min_qty()
                self._check_existing_open_promo()
            else:
                self._check_date_start()
                self._check_date_end()
                self._check_dates()
                self._check_existing_promo()

    @api.model_create_multi
    def create(self, vals_list):
        """
        When the record is created by import, the price is not always given...

        if not takes the default one
        """
        new_vals_list = []
        for vals in vals_list:
            if (
                not vals.get("price")
                and "partner_id" in vals
                and "product_tmpl_id" in vals
            ):
                vals["price"] = self._get_default_line(
                    vals["partner_id"], vals["product_tmpl_id"]
                ).price
                new_vals_list.append(vals)
        return super().create(new_vals_list)
