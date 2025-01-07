# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.alc_eshop_api_products_on_order import models

from ..exceptions import NoBackOrderOnBlanketOrderError


class AlcEshopProductOnOrder(models.AlcEshopProductOnOrder):

    def request_backorder_cancellation(self, quantity):
        for record in self:
            if record.order_id.order_type == "blanket":
                raise NoBackOrderOnBlanketOrderError(
                    record.product_id.name, record.order_ref, env=self.env
                )
        return super().request_backorder_cancellation(quantity)
