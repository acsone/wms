# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner

from .alc_product_promotion_subscription import AlcProductPromotionSubscription


class ResPartner(Partner):

    alc_product_promotion_subscription_ids = fields.One2many[
        AlcProductPromotionSubscription
    ](string="Product promotion subscriptions", inverse_name="partner_id")

    alc_product_promotion_subscription_count = fields.Integer(
        compute="_compute_alc_product_promotion_subscription_count",
        string="# of product promotion subscriptions",
        copy=False,
    )

    def _compute_alc_product_promotion_subscription_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.search([("id", "child_of", self.ids)])
        all_partners.read(["parent_id"])

        subscription_groups = self.env["alc.product.promotion.subscription"].read_group(
            domain=[("partner_id", "in", all_partners.ids)],
            fields=["partner_id"],
            groupby=["partner_id"],
        )
        for group in subscription_groups:
            partner = self.browse(group["partner_id"][0])
            while partner:
                if partner in self:
                    partner.alc_product_promotion_subscription_count += group[
                        "partner_id_count"
                    ]
                partner = partner.parent_id
