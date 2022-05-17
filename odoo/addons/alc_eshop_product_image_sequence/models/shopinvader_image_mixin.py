# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderImageMixin(models.AbstractModel):
    _inherit = "shopinvader.image.mixin"

    def _prepare_data_resize(self, thumbnail, image_relation):
        self.ensure_one()
        res = super(ShopinvaderImageMixin, self)._prepare_data_resize(
            thumbnail, image_relation
        )
        if "sequence" in image_relation._fields:
            res["sequence"] = image_relation.sequence or 0
        return res
