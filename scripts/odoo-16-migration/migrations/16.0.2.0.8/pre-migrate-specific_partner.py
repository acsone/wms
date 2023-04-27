# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _mig_partner_legal_form(env):
    models = [("legal.entity", "alc.partner.legal.form")]
    openupgrade.rename_models(env.cr, models)

    tables = [("legal_entity", "alc_partner_legal_form")]
    openupgrade.rename_tables(env.cr, tables)

    fields = [
        (
            "res.partner",
            "res_partner",
            "legal_entity_id",
            "legal_form_id",
        )
    ]
    openupgrade.rename_fields(env, fields)


def migrate(env):
    _mig_partner_legal_form(env)
