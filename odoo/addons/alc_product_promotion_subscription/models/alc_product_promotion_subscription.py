# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2 import IntegrityError

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.product.models.product_template import ProductTemplate


class AlcProductPromotionSubscription(models.Model):

    _name = "alc.product.promotion.subscription"
    _description = "Product Promotion Subscription"

    partner_id = fields.Many2one[Partner](string="Partner", ondelete="cascade")
    product_id = fields.Many2one[ProductProduct](string="Product", ondelete="cascade")
    product_tmpl_id = fields.Many2one[ProductTemplate](
        related="product_id.product_tmpl_id",
        store=True,
        readonly=True,
        ondelete="cascade",
    )
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
        except IntegrityError as error:
            raise UserError(
                _(
                    "Partner {partner_name} already subscribed to promotion on product {product_name}"
                ).format(partner_name=partner_name, product_name=product_name)
            ) from error

    @api.model
    def unsubscribe(self, partner, product):
        self.search(
            [("partner_id", "=", partner.id), ("product_id", "=", product.id)]
        ).unlink()
