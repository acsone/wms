# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        with self.sudo()._sync_rfa():
            res = super().write(vals)
            return res

    @api.model
    def _get_rfa_programs_domain(self):
        """Returns the base domain that all programs have to comply to."""
        company = self.env.company
        return [
            ("active", "=", True),
            ("sale_ok", "=", True),
            ("program_type", "=", "year_end_rebate"),
            ("company_id", "in", (company.id, company.parent_id.id, False)),
            "|",
            ("date_from", "=", False),
            ("date_from", "<=", fields.Date.context_today(self)),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", fields.Date.context_today(self)),
        ]

    def _get_rfa_programs(self):
        """Returns the programs that apply to the partner."""
        domain = self._get_rfa_programs_domain()
        return self.env["loyalty.program"].search(domain)

    def _get_partners_eligible_to_programs(self, programs):
        """Returns the partners that are eligible to the given programs."""
        partners = self.env["res.partner"]
        for partner in self:
            for program in programs:
                if program._is_partner_valid(partner):
                    partners |= partner
                    break
        return partners

    @contextmanager
    def _sync_rfa(self):
        """
        Context manager that ensures that if a partner is created or updated,.

        the RFA will be assigned to all sale orders of the partner confirmed
        after the signup date of the alcyonaire contract if the partner is
        eligible to the RFA program or the RFA will be removed if the partner
        is not eligible anymore.
        """
        rfa_programs = self._get_rfa_programs()
        eligible_partners = self._get_partners_eligible_to_programs(rfa_programs)
        new_eligible_partners = self.browse()
        yield
        new_eligible_partners = self._get_partners_eligible_to_programs(rfa_programs)
        to_add = new_eligible_partners - eligible_partners
        to_remove = eligible_partners - new_eligible_partners
        for partner in to_add:
            partner._assign_rfa(rfa_programs)
        for partner in to_remove:
            partner._remove_rfa(rfa_programs)

    def _assign_rfa(self, programs):
        """Assign the RFA to the partner."""
        for partner in self:
            orders = self.env["sale.order"].search(
                [
                    ("partner_id", "=", partner.id),
                    ("state", "in", ["sale", "done"]),
                    ("date_order", ">=", partner.date_start_contract_alcyonnaire),
                ]
            )
            for order in orders.with_context(
                ensure_program_valid_at_order_date=True,
                restricted_program_ids=programs.ids,
            ):
                order._update_programs_and_rewards(programs)

    def _remove_rfa(self, programs):
        """Remove the RFA from the partner."""
        loyalty_cards = self.env["loyalty.card"].search(
            [
                ("program_id", "in", programs.ids),
                ("partner_id", "in", self.ids),
            ]
        )
        loyalty_cards.sudo().unlink()
