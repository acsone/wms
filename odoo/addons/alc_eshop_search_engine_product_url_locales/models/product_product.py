# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.models import Model


class ProductProduct(Model):
    _name = "product.product"
    _inherit = ["product.product", "abstract.url.local"]
