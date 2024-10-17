# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api

from odoo.addons.purchase.models.purchase import PurchaseOrder as PurchaseOrderBase


class PurchaseOrder(PurchaseOrderBase):
    def button_compute_additional_products(self):
        """
        Compute additional products for a recordsets of purchae orders.

        In a first time, this method will delete all existing additional
        lines. After that, for each line, the method will check if we
        need to create an additional line.
        """
        # Remove existing additional lines. These lines will be
        # recomputed if needed
        self._remove_additional_lines()
        self.mapped("order_line")._compute_additional_products()

    def button_draft(self):
        """
        Remove additional product.

        :return:
        """
        result = super().button_draft()
        self._remove_additional_lines()
        return result

    def _remove_additional_lines(self):
        lines_to_remove = self.mapped("order_line").filtered("is_additional_product")
        lines_to_remove.unlink()

    @api.returns(None, lambda value: value[0])
    def copy_data(self, default=None):
        res = super().copy_data(default=default)
        # Skip additional lines on duplicate
        if "order_line" in res[0]:
            for i, line in reversed(list(enumerate(res[0]["order_line"]))):
                if not line[0] and line[2].get("is_additional_product"):
                    del res[0]["order_line"][i]
        return res
