# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta


class YearEndRebatePartnerVisibilityTestMixin:

    @classmethod
    def _setupRecords(cls):
        cls.veterinary_group_model = cls.env["veterinary.group"]
        cls.partner_model = cls.env["res.partner"]
        cls.alcyonnaire_group = cls.veterinary_group_model.create(
            {"name": "Alcyonnaire", "is_alcyonnaire": True}
        )
        cls.yesterday = datetime.now() - timedelta(days=1)

    @classmethod
    def _allow_partner_to_see_total_year_end_rebate(cls, partner, allow=True):
        """
        Set the required field to allow the partner to see or not.

        the total year end rebate
        """
        if not allow:
            partner.is_total_year_end_rebate_visible = False
        else:
            partner.is_total_year_end_rebate_visible = True
            partner.is_exclusive_vet_efficiency_member = True
            partner.veterinary_group_ids = cls.alcyonnaire_group
            partner.date_start_contract_alcyonnaire = cls.yesterday
