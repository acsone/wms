# Copyright 2023 ACSONE SA/NV
# License Other proprietary
from odoo import api, fields

from odoo.addons.account_intrastat.models.account_intrastat_code import (
    AccountIntrastatCode,
)
from odoo.addons.product.models.product_category import ProductCategory as Category


class ProductCategory(Category):

    intrastat_code_id = fields.Many2one[AccountIntrastatCode](
        string="Intrastat Code",
        compute="_compute_intrastat_code_id",
        store=True,
        recursive=True,
        readonly=True,
        help="This is the computed intrastat code from the value in specific field or"
        "from parent category",
    )
    specific_intrastat_code_id = fields.Many2one[AccountIntrastatCode](
        help="Fill in this in order to define a specific value for this category that"
        "should be different from the parent one."
    )

    @api.depends("parent_id.intrastat_code_id", "specific_intrastat_code_id")
    def _compute_intrastat_code_id(self):
        for category in self:
            if (
                category.specific_intrastat_code_id
                and category.specific_intrastat_code_id != category.intrastat_code_id
            ):
                category.intrastat_code_id = category.specific_intrastat_code_id
            elif (
                category.parent_id.intrastat_code_id
                and category.parent_id.intrastat_code_id != category.intrastat_code_id
            ):
                category.intrastat_code_id = category.parent_id.intrastat_code_id
            else:
                category.intrastat_code_id = False
