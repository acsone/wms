# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import date

from extendable_pydantic.models import StrictExtendableBaseModel

from odoo.addons.shopinvader_product.schemas.product import (
    ProductProduct as BaseProductProduct,
)


class TimeFrame(StrictExtendableBaseModel):
    gte: date | None
    lte: date | None


class LoyaltyRule(StrictExtendableBaseModel):
    time_frame: TimeFrame
    sequence: int
    program_id: int
    id: int


class ProductProduct(BaseProductProduct, extends=True):
    loyalty_rules: list[LoyaltyRule] = []

    @classmethod
    def from_product_product(cls, odoo_rec) -> ProductProduct:
        # at this time we take into account only products directly linked to a loyalty program
        obj = super().from_product_product(odoo_rec)
        all_rules = []
        for program, rules in odoo_rec.loyalty_rule_ids.partition("program_id").items():
            if not program.active:
                continue
            if program.date_to and program.date_to < date.today():
                continue
            for rule in rules:
                # the sequence should be an integer where
                # 1000 is the program sequence and 1-999 is the rule sequence
                # this is to ensure that the rules are ordered by program and then by rule
                sequence = (program.sequence or 1 * 1000) + (rule.sequence or 1)
                program_id = program.id
                all_rules.append(
                    LoyaltyRule(
                        time_frame=TimeFrame(
                            gte=program.date_from, lte=program.date_to
                        ),
                        sequence=sequence,
                        program_id=program_id,
                        id=rule.id,
                    )
                )

        obj.loyalty_rules = all_rules
        return obj
