# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.delivery.models import sale_order

from .delivery_carrier import DeliveryCarrier


class SaleOrder(sale_order.SaleOrder):
    def _get_available_carriers(self) -> DeliveryCarrier:
        """
        Get the available carriers for the current order.

        :return: recordset
        """
        return self.env["delivery.carrier"].search(
            [
                ("available_in_website", "=", True),
            ]
        )
