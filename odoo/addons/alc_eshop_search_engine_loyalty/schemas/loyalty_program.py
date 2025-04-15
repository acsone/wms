# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from extendable_pydantic import StrictExtendableBaseModel


class TimeFrame(StrictExtendableBaseModel):
    gte: date | None
    lte: date | None


class LoyaltyRuleDescr(StrictExtendableBaseModel):
    sequence: int
    id: int
    name: str
    program_id: int

    @classmethod
    def from_loyalty_rule(cls, odoo_rec):
        return cls.model_construct(
            sequence=odoo_rec.sequence,
            id=odoo_rec.id,
            name=odoo_rec.name,
            program_id=odoo_rec.program_id.id,
        )


class LoyaltyProgram(StrictExtendableBaseModel):
    id: int
    time_frame: TimeFrame
    name: str
    type: str
    sequence: int
    date_start: date
    date_end: date
    rules: list[LoyaltyRuleDescr] = []

    @classmethod
    def from_loyalty_program(cls, odoo_rec):
        return cls.model_construct(
            id=odoo_rec.id,
            name=odoo_rec.name,
            type=odoo_rec.program_type,
            sequence=odoo_rec.sequence,
            time_frame=TimeFrame(
                gte=odoo_rec.date_start,
                lte=odoo_rec.date_end,
            ),
            date_start=odoo_rec.date_start,
            date_end=odoo_rec.date_end,
            rules=[
                LoyaltyRuleDescr.from_loyalty_rule(rule)
                for rule in odoo_rec.rule_ids.sorted("sequence")
            ],
        )
