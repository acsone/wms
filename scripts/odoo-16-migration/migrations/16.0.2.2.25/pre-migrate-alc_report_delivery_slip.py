# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _migrate_data(cr):
    data = [
        (
            "specific_print.deliveryslip_orderref",
            "alc_report_delivery_slip.deliveryslip_orderref",
        ),
    ]
    openupgrade.rename_xmlids(cr, data, allow_merge=True)


def migrate(cr, version):
    _migrate_data(cr)
