# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.sale_exception.models.sale_order import SaleOrder as Order


class SaleOrder(Order):
    def sale_check_exception(self):
        # pylint: disable=except-pass
        try:
            self._check_exception()
        except ValidationError:
            # If a sale exception is found it will be displayed on the UI
            pass

    def detect_exceptions(self):
        non_blocking_as_exception = self._is_non_blocking_as_exception()
        all_exceptions = super().detect_exceptions()
        exceptions = self.env["exception.rule"].browse(all_exceptions)
        is_blocking = any(exception.is_blocking for exception in exceptions)
        if all_exceptions and not non_blocking_as_exception and not is_blocking:
            self.exception_ids = False
            return []
        return all_exceptions
