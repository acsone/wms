# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from odoo.addons.alc_eshop_schema_sale_discount import schemas
from odoo.addons.sale.models import sale_order_line


class SaleLineDiscount(schemas.SaleLineDiscount, extends=True):
    @classmethod
    def from_sale_order_line(
        cls, odoo_rec: sale_order_line.SaleOrderLine
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable):
        res = super().from_sale_order_line(odoo_rec)
        res.rate = odoo_rec._get_final_discount()
        return res


class SaleLineUnitPrice(schemas.SaleLineUnitPrice, extends=True):
    @classmethod
    def from_sale_order_line(
        cls, odoo_rec: sale_order_line.SaleOrderLine
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable):
        res = super().from_sale_order_line(odoo_rec)
        res.untaxed_with_discount = (
            odoo_rec.price_unit
            - odoo_rec.price_unit * (odoo_rec._get_final_discount() or 0) / 100
        )
        return res
