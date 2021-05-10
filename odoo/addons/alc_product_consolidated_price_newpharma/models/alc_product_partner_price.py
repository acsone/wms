# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AlcProductPartnerPrice(models.Model):

    _inherit = "alc.product.partner.price"

    @api.model
    def cron_generate_for_new_pharma(self):
        user = self.env["res.users"].search([("is_for_newpharma", "=", "True")])
        if not user:
            raise RuntimeError("Now newpharma user found!")
        domain = self.env.ref(
            "alc_product_consolidated_price_newpharma.newpharma_product_assortment_filter"
        )._get_eval_domain()
        partner_newpharam = user.partner_id
        self._compute_for_partner(partner=partner_newpharam, product_domain=domain)
