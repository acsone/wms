# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.alc_partner_manual_sale_order.models.res_partner import (
    ResPartner as ResPartnerBase,
)

B2C_CUSTOMER_CATEGORY_REF = "alc_b2c_partner.res_partner_category_b2c_customer"


class ResPartner(ResPartnerBase):

    is_b2c_customer = fields.Boolean(
        compute="_compute_is_b2c_customer",
        inverse="_inverse_is_b2c_customer",
        store=True,
        index=True,
    )
    manual_sale_order_allowed = fields.Boolean(
        compute="_compute_is_b2c_customer", store=True, readonly=False
    )

    @api.constrains("is_b2c_customer", "manual_sale_order_allowed")
    def _check_no_manual_sale_order_allowed_b2c_customer(self):
        errored = self.filtered(
            lambda p: p.is_b2c_customer and p.manual_sale_order_allowed
        )
        if errored:
            raise ValidationError(
                _(
                    "Manual sale order not allowed for B2C customers (%(name)s)",
                    name=errored.mapped("name"),
                )
            )

    @api.depends("category_id")
    def _compute_is_b2c_customer(self):
        bc2_category = self.env.ref(B2C_CUSTOMER_CATEGORY_REF, raise_if_not_found=False)
        if not bc2_category:
            # odoo init stage...
            self.update({"is_b2c_customer": False})
            return
        for rec in self:
            # In an onchange, id is an instance of odoo.models.NewId
            # use _origin to get db records
            rec.is_b2c_customer = bc2_category in rec.category_id._origin
            rec.manual_sale_order_allowed = not rec.is_b2c_customer

    def _inverse_is_b2c_customer(self):
        bc2_category = self.env.ref(B2C_CUSTOMER_CATEGORY_REF)
        to_unset = self.filtered(lambda n: not n.is_b2c_customer)
        to_unset.write(
            {
                "category_id": [Command.unlink(bc2_category.id)],
                "manual_sale_order_allowed": True,
            }
        )
        to_set = self.filtered(lambda n: n.is_b2c_customer)
        to_set.write(
            {
                "category_id": [Command.link(bc2_category.id)],
                "manual_sale_order_allowed": False,
            }
        )
