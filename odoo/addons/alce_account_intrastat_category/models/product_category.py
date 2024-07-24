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
                not category.specific_intrastat_code_id
                and category.parent_id.intrastat_code_id
            ):
                category.intrastat_code_id = category.parent_id.intrastat_code_id
            else:
                category.intrastat_code_id = category.specific_intrastat_code_id

    def _compute_all_category_intrastat_code(self):
        def _compute_intrastat_code(categ):
            categ._compute_intrastat_code_id()
            for child_catge in categ.child_id:
                _compute_intrastat_code(child_catge)

        for parent_categ in self.with_context(active_test=False).search(
            [("parent_id", "=", False)]
        ):
            _compute_intrastat_code(parent_categ)

        products = (
            self.env["product.product"].with_context(active_test=False).search([])
        )
        products._compute_intrastat_code_id()
