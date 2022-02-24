# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderCategory(models.Model):

    _inherit = "shopinvader.category"

    def _post_process_url_key(self, key):
        value = super(ShopinvaderCategory, self)._post_process_url_key(key)
        if not self.parent_id or not self.shopinvader_parent_id.active:
            # we are at the root category. We must add the prefix
            value = u"c/" + value
        return value
