# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_schema_sale import schemas


class SaleLineWithQtyUnavailableDiff(schemas.SaleLine):
    qty_unavailable_diff: int = 0


class SaleWithQtyUnavailableDiff(schemas.Sale):
    lines: list[SaleLineWithQtyUnavailableDiff]

    @classmethod
    def from_sale_order(cls, odoo_rec, qty_unavailable_diff: dict[int, float]):
        res = super().from_sale_order(odoo_rec)
        lines = []
        for sale_line in res.lines:
            line = SaleLineWithQtyUnavailableDiff.model_construct(
                **sale_line.model_dump(),
            )
            line.qty_unavailable_diff = qty_unavailable_diff.get(line.id, 0)
            lines.append(line)
        res.lines = lines
        return res
