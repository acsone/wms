# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.osv import expression

from odoo.addons.stock_available_to_promise_release.models.stock_location import (
    StockLocation as LocationBase,
)


class StockLocation(LocationBase):
    def _get_available_to_promise_domain(self):
        domain = super()._get_available_to_promise_domain()
        domain = expression.AND(
            [domain, [("location_id.exclude_from_immediately_usable_qty", "=", False)]]
        )
        return domain
