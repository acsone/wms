# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class LoyaltyRule(models.Model):

    _inherit = "loyalty.rule"

    program_type = fields.Selection(related="program_id.program_type", store=True)
    reward_point_max_amount = fields.Float(
        string="Reward Max",
        help="Maximum amount of points that can be earned with this rule."
        "This field is only used for year-end rebate programs when the potential"
        "points to earn are not known in advance and will depend on the volume of"
        "sales at the end of the year.",
        default=0.0,
    )

    @api.constrains("program_type", "product_domain")
    def _check_program_type(self):
        for rule in self:
            if (
                rule.program_type == "year_end_rebate"
                and rule.product_domain
                and rule.product_domain != "[]"
            ):
                raise ValidationError(
                    _(
                        "A rule with a product domain cannot be "
                        "applied on a year-end rebate program."
                    )
                )

    @api.constrains("program_type", "product_category_id")
    def _check_program_type_category(self):
        for rule in self:
            if rule.program_type == "year_end_rebate" and rule.product_category_id:
                raise ValidationError(
                    _(
                        "A rule with a product category cannot be "
                        "applied on a year-end rebate program."
                    )
                )

    @api.constrains("program_type", "product_tag_id")
    def _check_program_type_tag(self):
        for rule in self:
            if rule.program_type == "year_end_rebate" and rule.product_tag_id:
                raise ValidationError(
                    _(
                        "A rule with a product tag cannot be "
                        "applied on a year-end rebate program."
                    )
                )

    @api.constrains("program_type", "product_ids")
    def _check_program_type_product(self):
        for rule in self:
            if rule.program_type == "year_end_rebate" and not rule.product_ids:
                raise ValidationError(
                    _(
                        "You must select at least one product "
                        "to apply the rule on a year-end rebate program."
                    )
                )

    @api.constrains("program_type", "partner_domain")
    def _check_program_type_partner(self):
        for rule in self:
            if (
                rule.program_type == "year_end_rebate"
                and rule.partner_domain
                and rule.partner_domain != "[]"
            ):
                raise ValidationError(
                    _(
                        "A rule with a partner domain cannot be "
                        "applied on a year-end rebate program."
                    )
                )

    @api.constrains("program_type", "partner_ids")
    def _check_program_type_partner_ids(self):
        for rule in self:
            if rule.program_type == "year_end_rebate" and rule.partner_ids:
                raise ValidationError(
                    _(
                        "A rule restricted to specific partners cannot be "
                        "applied on a year-end rebate program."
                    )
                )
