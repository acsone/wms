# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.alc_b2c_connector.models.sale_order import SaleOrder
from odoo.addons.alc_b2c_connector.schemas.sale_order import SaleOrderCommon


class OrderCommon(SaleOrderCommon, extends=True):
    gls_parcel_shop: str | None = None

    @classmethod
    def from_sale_order(cls, sale_order: SaleOrder) -> "SaleOrderCommon":
        res = super().from_sale_order(sale_order)
        res.gls_parcel_shop = sale_order.gls_parcel_shop or None
        return res
