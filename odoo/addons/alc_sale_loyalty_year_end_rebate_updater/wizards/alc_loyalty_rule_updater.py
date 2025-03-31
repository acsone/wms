# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AlcLoyaltyRuleUpdater(models.TransientModel):
    _name = "alc.loyalty.rule.updater"
    _description = "Update Loyalty Rule"

    loyalty_program_id = fields.Many2one(
        "loyalty.program",
        string="Loyalty Program",
        required=True,
    )

    line_ids = fields.One2many(
        "alc.loyalty.rule.updater.line",
        "alc_loyalty_rule_updater_id",
        string="Update rules lines",
    )

    retroactive = fields.Boolean(
        string="Apply retroactively?",
    )
    retroactive_date = fields.Date(
        string="Retroactive Date",
        help="Date from which the new rule will be applied to past sales",
    )
    is_retroactive_date_required = fields.Boolean(
        compute="_compute_is_retroactive_date_required",
    )

    @api.constrains("retroactive_date", "retroactive")
    def _check_retroactive_date(self):
        for wizard in self:
            if wizard.retroactive and not wizard.retroactive_date:
                raise ValueError(_("Retroactive date is required"))

    @api.depends("retroactive")
    def _compute_is_retroactive_date_required(self):
        for wizard in self:
            wizard.is_retroactive_date_required = wizard.retroactive

    def do_update(self):
        touched_products = self.line_ids.do_update()
        if self.retroactive:
            self.loyalty_program_id._update_loyalty_points(
                touched_products, self.retroactive_date
            )
