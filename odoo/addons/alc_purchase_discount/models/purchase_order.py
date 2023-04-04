# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.purchase_discount.models.purchase_order import (
    PurchaseOrder as PurchaseOrderBase,
)


class PurchaseOrder(PurchaseOrderBase):
    def _add_supplier_to_product(self):
        """
        Disable this feature.

        :return:
        """
        return
