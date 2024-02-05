# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_merge_records


def _rename_alc_apb(env):
    """
    Merge l10n_be record in alc one as all account move lines have.

    that one for reference.
    Then, rename alc apb group tu use l10n_be_apb_tax module one.
    """

    l10n_apb = env.ref("l10n_be_apb_tax.tax_group_apb")
    alc_apb = env.ref("alc_accounting_data.tax_group_apb")
    openupgrade_merge_records.merge_records(
        env, "account.tax.group", [l10n_apb.id], alc_apb.id, method="sql"
    )

    xml_spec = [("alc_accounting_data.tax_group_apb", "l10n_be_apb_tax.tax_group_apb")]
    openupgrade.rename_xmlids(env.cr, xmlids_spec=xml_spec)


@openupgrade.migrate()
def migrate(env, version):
    _rename_alc_apb(env)
