# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(cr):
    data = [
        (
            "specific_print.paperformat_alcyon_report",
            "alc_report_base.paperformat_alcyon_report",
        ),
    ]
    openupgrade.rename_xmlids(cr, data, allow_merge=True)


def migrate(cr, version):
    _migrate_data(cr)
