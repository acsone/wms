# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockQuantPackage(models.Model):

    _inherit = "stock.quant.package"

    def write(self, vals):
        # Override the default implementation to avoid to write self as parent
        # of itself. This code is required since a package in a pack operation
        # could be used as detination package to avoid pack in pack when sending
        # package to GSL.... Pack in pack is not properly supported into odoo
        # 10. This code should be removes into odoo 14
        if "parent_id" in vals and vals["parent_id"] in self.ids:
            parent_id = vals["parent_id"]
            no_same_parent = self.filtered(lambda s, p=parent_id: s.id != p)
            if no_same_parent:
                super(StockQuantPackage, no_same_parent).write(vals)
            same_parent = self - no_same_parent
            v = vals.copy()
            v.pop("parent_id")
            return super(StockQuantPackage, same_parent).write(v)
        return super(StockQuantPackage, self).write(vals)
