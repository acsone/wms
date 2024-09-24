# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_package_type_category.models.stock_package_type_category import (
    StockPackageTypeCategory as Category,
)


class StockPackageTypeCategory(Category):

    show_in_delivery_slip_report = fields.Boolean()
    sequence_in_delivery_slip_report = fields.Integer()
