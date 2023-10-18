# Copyright 2021-2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields

from odoo.addons.product_abc_classification.models.abc_classification_profile import (
    AbcClassificationProfile,
)
from odoo.addons.stock.models.stock_package_type import PackageType


class StockPackageType(PackageType):

    abc_classification_profile_ids = fields.Many2many[AbcClassificationProfile](
        string="ABC Classification Profiles",
        relation="abc_classification_profile_stock_package_type_rel",
        column1="package_type_id",
        column2="profile_id",
    )
