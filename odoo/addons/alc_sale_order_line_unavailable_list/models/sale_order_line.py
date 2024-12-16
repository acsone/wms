# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from typing_extensions import Self

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as LineBase


class SaleOrderLine(LineBase):

    def search(self, domain, offset=0, limit=None, order=None, count=False) -> Self:
        """Sort by order date when displaying unavailable lines."""
        result = super().search(
            domain=domain, offset=offset, limit=limit, order=order, count=count
        )
        if isinstance(result, LineBase) and self.env.context.get("unavailable_list"):
            return result.sorted(lambda line: line.order_id.date_order, reverse=True)
        return result
