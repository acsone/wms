# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from odoo.addons.shopinvader_schema_sale.schemas import sale


class Sale(sale.Sale, extends=True):
    suite_name: str | None = None

    @classmethod
    def from_sale_order(
        cls, odoo_rec
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        res = super().from_sale_order(odoo_rec)
        res.suite_name = odoo_rec.suite_name or None
        return res
