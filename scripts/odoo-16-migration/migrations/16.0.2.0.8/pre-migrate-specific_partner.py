# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _mig_partner_legal_form(cr):
    models = [("legal.entity", "alc.partner.legal.form")]
    openupgrade.rename_models(cr, models)

    tables = [("legal_entity", "alc_partner_legal_form")]
    openupgrade.rename_tables(cr, tables)

    fields = [
        (
            "res.partner",
            "res_partner",
            "legal_entity_id",
            "legal_form_id",
        )
    ]
    openupgrade.rename_fields(cr, fields)


def migrate(cr, version):
    _mig_partner_legal_form(cr)
