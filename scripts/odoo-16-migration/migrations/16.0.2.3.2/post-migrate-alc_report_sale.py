# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

IDS = {
    "email_template_pharmacist_supplier_order",
    "mail_template_pharamcist_notification",
}


def _lock_data(cr):
    # set back records we've updated to noupdate=True
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data
        SET noupdate=true
        WHERE module='alc_report_sale'
        AND name IN %s
    """,
        (tuple(IDS),),
    )


@openupgrade.migrate()
def migrate(env, version):
    _lock_data(env.cr)
