# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.sale.models.sale_order_line import SaleOrderLine

from .base_model import BaseModel


class SaleLineCommon(BaseModel):
    sku: str
    line_id: int | None = None

    @classmethod
    def from_sale_order_line(cls, sale_line: SaleOrderLine) -> "SaleLineCommon":
        return cls.model_construct(
            sku=sale_line.product_id.default_code,
            line_id=int(sale_line.b2c_ref) if sale_line.b2c_ref else None,
        )


class SaleLineRequest(SaleLineCommon):
    quantity: float


class SaleLineResponse(SaleLineCommon):
    qty_ordered: float
    qty_returned: float
    qty_delivered: float
    qty_cancelled: float
    qty_backorder: float

    @classmethod
    def from_sale_order_line(cls, sale_line: SaleOrderLine) -> "SaleLineResponse":
        obj = super().from_sale_order_line(sale_line)
        obj.qty_ordered = sale_line.product_uom_qty
        obj.qty_returned = sale_line.product_qty_returned
        obj.qty_delivered = sale_line.qty_delivered
        obj.qty_cancelled = sale_line.product_qty_canceled
        obj.qty_backorder = sale_line.product_qty_backorder
        return obj
