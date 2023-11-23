# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _move_apb(cr):
    fieldspec = [("specific_account.tax_group_apb", "l10n_be_apb_tax.tax_group_apb")]
    openupgrade.rename_xmlids(cr, fieldspec)


def migrate(cr, version):
    _move_apb(cr)
