# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        """
        UPDATE account_move am
        SET mandate_id = aml.mandate_id
        FROM account_move_line aml
        WHERE aml.mandate_id IS NOT NULL
            AND am.mandate_id IS NULL
            AND am.id=aml.move_id
        """
    )
