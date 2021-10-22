# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShopinvaderProduct(models.Model):
    _inherit = "shopinvader.product"

    def _get_categories(self):
        res = super(ShopinvaderProduct, self)._get_categories()
        return res.filtered(lambda c: c.is_web)
