# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.osv.expression import AND

from odoo.addons.product_expiry.models.stock_quant import StockQuant as StockQuantBase


class StockQuant(StockQuantBase):
    def _get_gather_domain(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
    ):
        domain = super()._get_gather_domain(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
        )
        removal_date_limit = self.env.context.get("removal_date_limit")
        if removal_date_limit:
            return AND(
                [
                    domain,
                    [
                        "|",
                        ("removal_date", "=", False),
                        ("removal_date", ">=", removal_date_limit),
                    ],
                ]
            )
        return domain
