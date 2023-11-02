# Copyright 2023 ACSONE SA/NV
# License Other proprietary
from odoo import fields

from odoo.addons.account_intrastat.models.account_intrastat_code import (
    AccountIntrastatCode,
)
from odoo.addons.product.models.product_template import ProductTemplate as Product


class ProductTemplate(Product):

    specific_intrastat_code_id = fields.Many2one[AccountIntrastatCode](
        string="Specific Intrastat Code",
        related="product_variant_ids.specific_intrastat_code_id",
        help="This is the Intrastat Code that should not come from the"
        "product category.",
    )
