# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.alc_eshop_search_engine_loyalty.schemas import loyalty_program


class LoyaltyProgram(loyalty_program.LoyaltyProgram, extends=True):
    is_public: bool

    @classmethod
    def from_loyalty_program(cls, odoo_rec):
        res = super().from_loyalty_program(odoo_rec)
        res.is_public = odoo_rec.is_public
        return res
