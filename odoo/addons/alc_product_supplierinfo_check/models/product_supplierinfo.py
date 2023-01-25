# Copyright 2017 Julien Coux (Camptocamp)
# Copyright 2023 ACSONE SA/NV
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

    def _check_unique_supplier(self):
        self.ensure_one()
        other_supplier = self.search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("partner_id", "!=", self.partner_id.id),
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

    @api.constrains("date_start", "date_end", "partner_id", "min_qty", "min_qty_sale")
    def check_dates(self):
        # Used by imports to avoid problems with imported data
        if self._context.get("disable_check_dates"):
            return
        for rec in self:
            rec._check_unique_supplier()
            if not rec.date_start and not rec.date_end:
                rec._check_min_qty()
                rec._check_existing_open_promo()
            else:
                rec._check_date_start()
                rec._check_date_end()
                rec._check_dates()
                rec._check_existing_promo()
