# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_b2c_customer = fields.Boolean(
        compute="_compute_is_b2c_customer",
        inverse="_inverse_is_b2c_customer",
        store=True,
        index=True,
    )

    @api.constrains("is_b2c_customer", "manual_sale_order_allowed")
    def _check_no_manual_sale_order_allowed_b2c_customer(self):
        errored = self.filtered(
            lambda p: p.is_b2c_customer and p.manual_sale_order_allowed
        )
        if errored:
            raise ValidationError(
                _("Manual sale order not allowed for B2C cutomers (%s)")
                % errored.mapped("name")
            )

    @api.depends("category_id")
    def _compute_is_b2c_customer(self):
        bc2_category = self.env.ref(
            "alc_b2c_partner.res_partner_category_b2c_customer",
            raise_if_not_found=False,
        )
        if not bc2_category:
            # odoo init stage...
            for rec in self:
                rec.is_b2c_customer = False
            return
        for rec in self:
            rec.is_b2c_customer = bc2_category in rec.category_id

    def _inverse_is_b2c_customer(self):
        bc2_category_id = self.env.ref(
            "alc_b2c_partner.res_partner_category_b2c_customer"
        ).id
        to_unset = self.filtered(lambda n: not n.is_b2c_customer)
        to_unset.write({"category_id": [(3, bc2_category_id)]})
        to_set = self.filtered(lambda n: n.is_b2c_customer)
        to_set.write({"category_id": [(4, bc2_category_id)]})

    @api.onchange("is_b2c_customer", "category_id")
    def _onchange_b2c(self):
        bc2_category_id = self.env.ref(
            "alc_b2c_partner.res_partner_category_b2c_customer"
        )
        for record in self:
            if record.is_b2c_customer or bc2_category_id in record.category_id:
                record.manual_sale_order_allowed = False

    @api.multi
    def _write(self, vals):
        if vals.get("is_b2c_customer"):
            vals["manual_sale_order_allowed"] = False
        return super(ResPartner, self)._write(vals)
