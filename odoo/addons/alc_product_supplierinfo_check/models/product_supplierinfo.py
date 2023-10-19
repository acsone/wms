# Copyright 2017 Julien Coux (Camptocamp)
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from ast import literal_eval

from odoo import _, api
from odoo.exceptions import ValidationError

from odoo.addons.product.models.product_supplierinfo import SupplierInfo


class ProductSupplierinfo(SupplierInfo):
    def _check_unique_supplier(self):
        self.ensure_one()
        other_supplier = self.search(
            [
                ("product_tmpl_id", "=", self.product_tmpl_id.id),
                ("partner_id", "!=", self.partner_id.id),
            ]
        )
        if other_supplier:
            raise ValidationError(
                _("You cannot have two different supplier for a product")
            )

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
                _("You cannot have two promos without start and end date")
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

    @api.model
    def _is_alcyon_constraints_check_activated(self):
        return not self._context.get("disable_check_dates") and literal_eval(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "alc_product_supplierinfo_check.check_alcyon_constraints_on_supplierinfo",
                "False",
            )
        )

    @api.constrains("date_start", "date_end", "partner_id", "min_qty", "min_qty_sale")
    def check_dates(self):
        # Used by imports to avoid problems with imported data
        if not self._is_alcyon_constraints_check_activated():
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
