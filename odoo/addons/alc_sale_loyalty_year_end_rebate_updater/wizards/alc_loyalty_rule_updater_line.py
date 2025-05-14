# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command, _, api, fields, models
from odoo.osv.expression import FALSE_DOMAIN, TRUE_DOMAIN


class AlcLoyaltyRuleUpdaterLine(models.TransientModel):
    _name = "alc.loyalty.rule.updater.line"
    _description = "Loyalty Rule Update Line"

    alc_loyalty_rule_updater_id = fields.Many2one(
        "alc.loyalty.rule.updater",
        string="Loyalty Rule Updater",
        required=True,
        ondelete="cascade",
    )
    update_type = fields.Selection(
        [
            ("add_rule", "Add a new rule"),
            ("remove_rule", "Remove a rule"),
            ("rule_update_points", "Update points"),
            ("rule_add_products", "Update products"),
            ("rule_remove_products", "Remove products"),
        ],
        string="Update Type",
        required=True,
    )
    loyalty_rule_id = fields.Many2one(
        "loyalty.rule",
        string="Loyalty Rule",
    )
    is_loyalty_rule_required = fields.Boolean(
        compute="_compute_is_loyalty_rule_required",
    )
    new_reward_point_max_amount = fields.Float(
        string="New Reward Point Max Amount",
    )
    new_reward_point_amount = fields.Float(
        string="New Reward Point Amount",
    )
    is_points_required = fields.Boolean(
        compute="_compute_is_points_required",
    )
    added_product_ids = fields.Many2many(
        "product.product",
        string="New Products",
        relation="alc_loyalty_rule_updater_line_added_product_rel",
    )
    added_product_ids_domain = fields.Binary(
        compute="_compute_added_product_ids_domain"
    )
    is_added_product_required = fields.Boolean(
        compute="_compute_is_added_product_required",
    )
    removed_product_ids = fields.Many2many(
        "product.product",
        string="Products to Remove",
        relation="alc_loyalty_rule_updater_line_removed_product_rel",
    )
    removed_product_ids_domain = fields.Binary(
        compute="_compute_removed_product_ids_domain"
    )

    is_removed_product_required = fields.Boolean(
        compute="_compute_is_removed_product_required",
    )
    rule_name = fields.Char()
    is_rule_name_required = fields.Boolean(
        compute="_compute_is_rule_name_required",
    )
    loyalty_program_id = fields.Many2one(
        related="alc_loyalty_rule_updater_id.loyalty_program_id",
    )

    @api.constrains("update_type", "loyalty_rule_id")
    def _check_loyalty_rule_id(self):
        for record in self:
            if record.is_loyalty_rule_required and not record.loyalty_rule_id:
                raise ValueError(_("Loyalty Rule is required for this update type"))
            if not record.is_loyalty_rule_required and record.loyalty_rule_id:
                raise ValueError(
                    _("Loyalty Rule should not be set for this update type")
                )

    @api.constrains(
        "update_type", "new_reward_point_max_amount", "new_reward_point_amount"
    )
    def _check_points(self):
        for record in self:
            if (
                record.is_points_required
                and not (
                    record.new_reward_point_max_amount or record.new_reward_point_amount
                )
                and record.loyalty_program_id.program_type != "year_end_rebate"
            ):
                raise ValueError(_("Points are required for this update type"))
            if (
                not record.is_points_required
                and (
                    record.new_reward_point_max_amount or record.new_reward_point_amount
                )
                and record.loyalty_program_id.program_type != "year_end_rebate"
            ):
                raise ValueError(_("Points should not be set for this update type"))

    @api.constrains("update_type", "added_product_ids")
    def _check_added_products(self):
        for record in self:
            if record.is_added_product_required and not record.added_product_ids:
                raise ValueError(_("Products are required for this update type"))
            if not record.is_added_product_required and record.added_product_ids:
                raise ValueError(_("Products should not be set for this update type"))

    @api.constrains("update_type", "removed_product_ids")
    def _check_removed_products(self):
        for record in self:
            if record.is_removed_product_required and not record.removed_product_ids:
                raise ValueError(_("Products are required for this update type"))
            if not record.is_removed_product_required and record.removed_product_ids:
                raise ValueError(_("Products should not be set for this update type"))

    @api.constrains("update_type", "rule_name")
    def _check_rule_name(self):
        for record in self:
            if record.is_rule_name_required and not record.rule_name:
                raise ValueError(_("Rule name is required for this update type"))
            if not record.is_rule_name_required and record.rule_name:
                raise ValueError(_("Rule name should not be set for this update type"))

    @api.depends("update_type", "loyalty_rule_id")
    def _compute_removed_product_ids_domain(self):
        for wizard in self:
            if wizard.loyalty_rule_id and wizard.update_type == "rule_remove_products":
                wizard.removed_product_ids_domain = [
                    ("id", "in", wizard.loyalty_rule_id.product_ids.ids)
                ]
            else:
                wizard.removed_product_ids_domain = FALSE_DOMAIN

    @api.depends("update_type", "loyalty_rule_id")
    def _compute_added_product_ids_domain(self):
        for wizard in self:
            domain = FALSE_DOMAIN
            if wizard.loyalty_rule_id and wizard.update_type == "rule_add_products":
                domain = [("id", "not in", wizard.loyalty_rule_id.product_ids.ids)]
            elif wizard.update_type == "add_rule":
                product_ids = self.loyalty_program_id.rule_ids.product_ids
                if product_ids:
                    domain = [("id", "not in", product_ids.ids)]
                else:
                    domain = TRUE_DOMAIN
            wizard.added_product_ids_domain = domain

    @api.depends("update_type")
    def _compute_is_loyalty_rule_required(self):
        for record in self:
            record.is_loyalty_rule_required = record.update_type in [
                "remove_rule",
                "rule_add_products",
                "rule_remove_products",
                "rule_update_points",
            ]

    @api.depends("update_type")
    def _compute_is_points_required(self):
        for record in self:
            record.is_points_required = record.update_type in [
                "rule_update_points",
                "add_rule",
            ]

    @api.depends("update_type")
    def _compute_is_added_product_required(self):
        for record in self:
            record.is_added_product_required = record.update_type in [
                "rule_add_products",
                "add_rule",
            ]

    @api.depends("update_type")
    def _compute_is_removed_product_required(self):
        for record in self:
            record.is_removed_product_required = (
                record.update_type == "rule_remove_products"
            )

    @api.depends("update_type")
    def _compute_is_rule_name_required(self):
        for record in self:
            record.is_rule_name_required = record.update_type in ["add_rule"]

    @api.onchange("update_type")
    def _onchange_update_type(self):
        for record in self:
            if not record.is_loyalty_rule_required:
                record.loyalty_rule_id = False
            if not record.is_points_required:
                record.new_reward_point_max_amount = False
                record.new_reward_point_amount = False
            if not record.is_added_product_required:
                record.added_product_ids = [(5,)]
            if not record.is_removed_product_required:
                record.removed_product_ids = [(5,)]
            if not record.is_rule_name_required:
                record.rule_name = ""

    @api.onchange("loyalty_rule_id", "update_type")
    def _onchange_loyalty_rule_id(self):
        for record in self:
            if record.update_type != "rule_update_points":
                continue
            record.new_reward_point_max_amount = (
                record.loyalty_rule_id.reward_point_max_amount
            )
            record.new_reward_point_amount = record.loyalty_rule_id.reward_point_amount

    def do_update(self):
        """Do the actual update and return the list of products impacted by the update."""
        touched_products = self.env["product.product"]
        for record in self:
            touched_products |= getattr(record, f"_do_{record.update_type}")()
        return touched_products

    def _do_add_rule(self):
        self.ensure_one()
        rule = self.env["loyalty.rule"].create(
            {
                "program_id": self.loyalty_program_id.id,
                "reward_point_max_amount": self.new_reward_point_max_amount,
                "reward_point_amount": self.new_reward_point_amount,
                "product_ids": [Command.set(self.added_product_ids.ids)],
                "name": self.rule_name,
                "reward_point_mode": "money",
                "minimum_qty": 1,
            }
        )
        return rule.product_ids

    def _do_remove_rule(self):
        self.ensure_one()
        touched_products = self.loyalty_rule_id.product_ids
        self.loyalty_rule_id.unlink()
        return touched_products

    def _do_rule_update_points(self):
        self.ensure_one()
        touched_products = self.loyalty_rule_id.product_ids
        self.loyalty_rule_id.write(
            {
                "reward_point_max_amount": self.new_reward_point_max_amount,
                "reward_point_amount": self.new_reward_point_amount,
            }
        )
        return touched_products

    def _do_rule_add_products(self):
        self.ensure_one()
        self.loyalty_rule_id.write(
            {
                "product_ids": [
                    Command.link(product.id) for product in self.added_product_ids
                ]
            }
        )
        return self.added_product_ids

    def _do_rule_remove_products(self):
        self.ensure_one()
        self.loyalty_rule_id.write(
            {
                "product_ids": [
                    Command.unlink(product.id) for product in self.removed_product_ids
                ]
            }
        )
        return self.removed_product_ids
