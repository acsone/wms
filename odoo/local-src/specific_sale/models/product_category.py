# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.multi
    def has_for_parent(self, category_id):
        """Check if category_id is itself or a parent."""
        self.ensure_one()
        c = self
        while True:
            if c.id == category_id:
                return True
            if not c.parent_id:
                return False
            c = c.parent_id
        return False
