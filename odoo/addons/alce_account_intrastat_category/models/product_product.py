# Copyright 2023 ACSONE SA/NV
# License Other proprietary
from odoo import api, fields

from odoo.addons.account_intrastat.models.account_intrastat_code import (
    AccountIntrastatCode,
)
from odoo.addons.product.models.product_product import ProductProduct as Product


class ProductProduct(Product):

    intrastat_code_id = fields.Many2one[AccountIntrastatCode](
        compute="_compute_intrastat_code_id",
        store=True,
        readonly=True,
    )
    specific_intrastat_code_id = fields.Many2one[AccountIntrastatCode](
        string="Specific Intrastat Code",
        help="This is the Intrastat Code that should not come from the"
        "product category.",
    )

    @api.depends("categ_id.intrastat_code_id", "specific_intrastat_code_id")
    def _compute_intrastat_code_id(self):
        for product in self:
            if (
                not product.specific_intrastat_code_id
                and product.categ_id.intrastat_code_id
            ):
                product.intrastat_code_id = product.categ_id.intrastat_code_id
            else:
                product.intrastat_code_id = product.specific_intrastat_code_id
