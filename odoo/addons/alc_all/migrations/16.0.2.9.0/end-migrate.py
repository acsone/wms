# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def migrate(cr, version):
    """Activate the UBL payment method constraint."""

    query = """
    UPDATE res_company
        SET ubl_payment_mode_required = True
        WHERE ubl_payment_mode_required = False
      """
    openupgrade.logged_query(cr, query)
