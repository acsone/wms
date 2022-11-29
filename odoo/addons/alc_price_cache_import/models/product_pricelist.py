# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model
    def load(self, fields, data):
        """Batch price re-computation that happen with consecutive writes."""
        self_no_update = self.with_context(no_update_price_cache=True)
        res = super(ProductPricelist, self_no_update).load(fields, data)
        eids = None
        if "item_ids/id" in fields:
            index = fields.index("item_ids/id")
            eids = [self.env.ref(d[index]).id for d in data]
        self.browse(res["ids"]).delay_update_price_cache(eids=eids)
        return res
