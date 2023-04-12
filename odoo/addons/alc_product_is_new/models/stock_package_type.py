# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_package_type import PackageType


class StockPackageType(PackageType):

    is_new = fields.Boolean(default=False)
