# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.stock_storage_type.models.stock_quant_package import (
    StockQuantPackage as StockQuantPackageBase,
)


class StockQuantPackage(StockQuantPackageBase):
    def _sync_package_type_from_single_product(self):
        return super(
            StockQuantPackage, self.filtered(lambda p: not p.number_of_parcels)
        )._sync_package_type_from_single_product()
