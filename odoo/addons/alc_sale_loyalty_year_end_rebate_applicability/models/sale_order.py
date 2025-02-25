# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def _get_program_domain(self):
        domain = super()._get_program_domain()
        new_domain = []
        if self.env.context.get("ensure_program_valid_at_order_date"):
            for leaf in domain:
                if len(leaf) != 3:
                    new_domain.append(leaf)
                    continue
                field, operator, value = leaf
                if field in ("date_from", "date_to") and not isinstance(value, bool):
                    value = (
                        self.date_order
                        if self.date_order
                        else fields.Date.context_today(self)
                    )
                new_domain.append((field, operator, value))
            domain = new_domain
        program_ids = self.env.context.get("restricted_program_ids")
        if program_ids:
            domain.append(("id", "in", program_ids))
        return domain
