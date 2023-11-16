# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.delivery.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    def _is_delivery_method_available(self, method_id):
        """Check if the method is available for the given SO."""
        return self.env["delivery.carrier"].browse(method_id).exists()
