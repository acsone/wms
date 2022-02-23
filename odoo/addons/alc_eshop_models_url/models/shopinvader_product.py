# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderProduct(models.Model):

    _inherit = "shopinvader.product"

    def _post_process_url_key(self, key):
        value = super(ShopinvaderProduct, self)._post_process_url_key(key)
        return u"p/" + value
