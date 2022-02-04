# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.base_m2m_custom_field.fields import Many2manyCustom


class ResPartner(models.Model):

    _inherit = "res.partner"

    alc_product_promotion_subscription_ids = Many2manyCustom(
        string="Product promotion subscriptions",
        comodel_name="alc.product.promotion.subscription",
        relation="alc_product_promotion_subscription",
        column1="partner_id",
        column2="product_id",
        create_table=False,
        copy=False,
    )

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
