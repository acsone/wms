# Copyright 2022 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_storage_type.models import stock_package_type


class StockPackageType(stock_package_type.StockPackageType):

    is_new = fields.Boolean(default=False)
