# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    loyalty_rule_ids = fields.Many2many(
        comodel_name="loyalty.rule",
        relation="loyalty_rule_product_product_rel",
        column1="product_product_id",
        column2="loyalty_rule_id",
        string="Loyalty Rules",
        readonly=True,
    )
