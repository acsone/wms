# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale_exception.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    def _is_sale_exception_check_enabled(self):
        return self.env["ir.config_parameter"].get_param(
            "alc_sale_exception_settings.sale_exception_check_enabled"
        )

    def _check_sale_check_exception(self, vals):
        if not self._is_sale_exception_check_enabled():
            return None
        return super()._check_sale_check_exception(vals)

    def detect_exceptions(self):
        if not self._is_sale_exception_check_enabled():
            return None
        return super().detect_exceptions()

    def _check_exception(self):
        if not self._is_sale_exception_check_enabled():
            return None
        return super()._check_exception()
