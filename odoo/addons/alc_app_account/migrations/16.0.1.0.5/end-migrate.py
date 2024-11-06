# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _add_parameter(env):
    companies = env["res.company"].search([])
    companies.write({"restrict_partner_mismatch_on_reconcile": True})


@openupgrade.migrate()
def migrate(env, version):
    _add_parameter(env)
