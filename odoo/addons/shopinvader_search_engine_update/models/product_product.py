# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class ProductProduct(models.Model):

    _inherit = "product.product"

    def write(self, vals):
        # maybe do something more clever?
        res = super(ProductProduct, self).write(vals)
        if self.mapped("shopinvader_bind_ids"):
            self.mapped("shopinvader_bind_ids").write({"sync_state": "to_update"})
        return res
