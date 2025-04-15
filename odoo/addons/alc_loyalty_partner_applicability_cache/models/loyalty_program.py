# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class LoyaltyProgram(models.Model):

    _inherit = "loyalty.program"

    all_restricted_partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="loyalty_program_partner_rel",
        column1="loyalty_program_id",
        column2="partner_id",
        string="All Partners",
        compute="_compute_all_restricted_partner_ids",
        store=True,
        help="All partners that are eligible for this loyalty program.\n"
        "This field is used to cache the partner eligibility for the loyalty program.\n"
        "It is automatically updated when the program is created or modified. "
        "It's also modified when a partner is created or modified and by a daily cron.\n"
        "The list is empty if the program is not active or if the program is "
        "not restricted to specific partners.\n",
    )

    is_public = fields.Boolean(
        string="Public",
        help="This program is available for all partners.",
        compute="_compute_is_public",
        store=True,
        default=True,
    )

    @api.depends("partner_ids", "partner_domain", "is_public", "active")
    def _compute_all_restricted_partner_ids(self):
        """Compute the list of all partners that are eligible for this loyalty program."""
        for record in self:
            if record.is_public or not record.active:
                record.all_restricted_partner_ids = record.env["res.partner"]
            else:
                existing_partners = record.all_restricted_partner_ids
                new_all_partners = record.partner_ids
                if record.partner_domain and record.partner_domain != "[]":
                    domain = record._get_eval_partner_domain()
                    new_all_partners |= record.env["res.partner"].search(domain)
                partners_to_add = new_all_partners - existing_partners
                partners_to_remove = existing_partners - new_all_partners
                update_commands = []
                if partners_to_add:
                    update_commands.extend(
                        Command.link(partner.id) for partner in partners_to_add
                    )
                if partners_to_remove:
                    update_commands.extend(
                        Command.unlink(partner.id) for partner in partners_to_remove
                    )
                if update_commands:
                    record.all_restricted_partner_ids = update_commands
                partners_to_add.invalidate_recordset(["restricted_loyalty_program_ids"])
                partners_to_remove.invalidate_recordset(
                    ["restricted_loyalty_program_ids"]
                )

    @api.depends("partner_ids", "partner_domain")
    def _compute_is_public(self):
        """Compute if the program is public or not."""
        for record in self:
            record.is_public = record.partner_domain == "[]" and not record.partner_ids
