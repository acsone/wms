# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProductCategory(models.Model):
    _inherit = "product.category"

    def unlink(self):
        to_delete_characteristics = self.env["alc.product.characteristic"].search(
            [
                ("value_res_model", "=", self._name),
                ("value_res_id", "in", [record.id for record in self]),
            ]
        )
        to_delete_characteristics.unlink()
        res = super().unlink()
        return res
