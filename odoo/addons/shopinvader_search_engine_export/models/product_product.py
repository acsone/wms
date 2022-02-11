# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def shopinvader_manual_export(self):
        bindings = self.with_context(active_test=False).mapped("shopinvader_bind_ids")
        bindings.recompute_json()
        bindings.synchronize()
