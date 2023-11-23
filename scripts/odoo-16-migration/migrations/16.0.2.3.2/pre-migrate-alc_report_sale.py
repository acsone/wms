# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

IDS = {
    "email_template_pharmacist_supplier_order",
    "mail_template_pharamcist_notification",
}


def _move_data(cr):
    data = []
    for xmlid in IDS:
        data.append((f"specific_report.{xmlid}", f"alc_report_sale.{xmlid}"))
    openupgrade.rename_xmlids(cr, data, allow_merge=True)


def _unlock_data(cr):
    # set labels we want to update to noupdate=False
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data
        SET noupdate=false
        WHERE module='alc_report_sale'
        AND name IN %s
    """,
        (tuple(IDS),),
    )


def migrate(cr, version):
    _move_data(cr)
    _unlock_data(cr)
