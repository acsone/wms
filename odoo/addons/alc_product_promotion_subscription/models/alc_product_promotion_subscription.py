# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AlcProductPromotionSubscription(models.Model):

    _name = "alc.product.promotion.subscription"

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    product_id = fields.Many2one(comodel_name="product.product", string="Product")
    active = fields.Boolean(compute="_compute_active", store=True)

    _sql_constraints = [
        (
            "promotion_unique_subscription",
            "unique (partner_id, product_id)",
            _("You're already subscribed to the promotions for this product."),
        ),
    ]

    @api.depends("partner_id.active", "product_id.active")
    def _compute_active(self):
        for rec in self:
            rec.active = rec.partner_id.active and rec.product_id.active

    @api.model
    def subscribe(self, partner, product):
        partner_name = partner.name
        product_name = product.name
        try:
            return self.create({"partner_id": partner.id, "product_id": product.id})
        except IntegrityError:
            raise UserError(
                _("Partner %s already subscribed to promotion on product %s")
                % (partner_name, product_name)
            )

    @api.model
    def unsubscribe(self, partner, product):
        self.search(
            [("partner_id", "=", partner.id), ("product_id", "=", product.id)]
        ).unlink()
