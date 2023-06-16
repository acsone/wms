# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _unset_attachment(env):
    """Remove former value (was in specific report)."""
    # TODO: Remove this after migrating specific_report
    report = env.ref("sale.report_saleorder")
    report.attachment = ""


@openupgrade.migrate()
def migrate(env, version):
    _unset_attachment(env)
