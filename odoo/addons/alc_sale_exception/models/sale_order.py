# Copyright 2016 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from odoo.addons.sale_exception.models import sale_order


class SaleOrder(sale_order.SaleOrder):
    def sale_check_exception(self):
        # pylint: disable=except-pass
        try:
            self._check_exception()
        except ValidationError:
            # If a sale exception is found it will be displayed on the UI
            pass
