# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, models


class SeIndex(models.Model):

    _inherit = "se.index"

    @api.model
    def recompute_all_index(self, domain=None):
        if domain is None:
            domain = []
        domain.append(
            ("model_id", "!=", self.env.ref("alc_eshop_ads.model_alc_eshop_ads").id,)
        )
        return self.search(domain).recompute_all_binding()
