# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock_storage_type.models import product_template
from odoo.addons.stock_storage_type.models.stock_package_type import StockPackageType


class ProductTemplate(product_template.ProductTemplate):

    package_type_id = fields.Many2one[StockPackageType](tracking=True)
