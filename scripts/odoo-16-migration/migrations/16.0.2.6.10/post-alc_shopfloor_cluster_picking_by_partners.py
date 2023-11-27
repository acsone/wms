# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        """
        ALTER TABLE shopfloor_menu
        ADD COLUMN IF NOT EXISTS batch_group_by_commercial_partner BOOLEAN;
        UPDATE shopfloor_menu
        SET batch_group_by_commercial_partner=group_pickings_by_partner;
    """
    )
