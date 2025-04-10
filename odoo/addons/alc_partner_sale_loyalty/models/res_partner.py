# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.osv.expression import OR


class ResPartner(models.Model):

    _inherit = "res.partner"

    loyalty_cards_count = fields.Integer(
        string="Loyalty Cards", compute="_compute_loyalty_cards_count"
    )

    def _get_loyalty_card_domain(self):
        self.ensure_one()
        invoice_partner = self.address_get(["invoice"]).get("invoice", self)
        return OR(
            [
                [
                    ("beneficiary_partner_type", "=", "partner"),
                    ("partner_id", "=", self.id),
                ],
                [
                    ("beneficiary_partner_type", "=", "invoiced_partner"),
                    ("partner_id", "=", invoice_partner),
                ],
                [
                    ("beneficiary_partner_type", "=", "commercial_entity"),
                    ("partner_id", "=", self.commercial_partner_id.id),
                ],
            ]
        )

    def action_open_loyalty_cards(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "loyalty.loyalty_card_action"
        )
        action["domain"] = self._get_loyalty_card_domain()
        return action

    def _compute_loyalty_cards_count(self):
        self.ensure_one()
        loyalty_card = self.env["loyalty.card"]
        domain = self._get_loyalty_card_domain()
        self.loyalty_cards_count = loyalty_card.search_count(domain)
