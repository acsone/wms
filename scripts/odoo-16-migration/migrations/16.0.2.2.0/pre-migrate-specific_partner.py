# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    fields = [
        (
            "helpdesk.ticket",
            "helpdesk_ticket",
            "account_invoice_id",
            "account_move_id",
        )
    ]
    openupgrade.rename_fields(env, fields)
