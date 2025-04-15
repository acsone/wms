# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    restricted_loyalty_program_ids = fields.Many2many(
        comodel_name="loyalty.program",
        relation="loyalty_program_partner_rel",
        column1="partner_id",
        column2="loyalty_program_id",
        string="Restricted Loyalty Programs",
    )

    def _update_restricted_loyalty_programs(self):
        self_sudo = self.sudo()
        all_restricted_programs = self_sudo.env["loyalty.program"].search(
            [
                ("is_public", "=", False),
            ]
        )
        for record in self_sudo:
            restricted_programs = self_sudo.env["loyalty.program"]
            for program in all_restricted_programs:
                if record in program.partner_ids or record.filtered_domain(
                    program._get_eval_partner_domain()
                ):
                    restricted_programs |= program
            programs_to_remove = (
                record.restricted_loyalty_program_ids - restricted_programs
            )
            programs_to_add = (
                restricted_programs - record.restricted_loyalty_program_ids
            )
            update_commands = []
            if programs_to_add:
                update_commands.extend(
                    Command.link(program.id) for program in programs_to_add
                )
            if programs_to_remove:
                update_commands.extend(
                    Command.unlink(program.id) for program in programs_to_remove
                )
            if update_commands:
                record.restricted_loyalty_program_ids = update_commands

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        partners._update_restricted_loyalty_programs()
        return partners

    def write(self, vals):
        res = super().write(vals)
        self._update_restricted_loyalty_programs()
        return res
