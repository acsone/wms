# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _enable_auto_reconcile_mode(env):
    domiciliation = env.ref(
        "__setup__.account_payment_mode_1", raise_if_not_found=False
    )
    if not domiciliation:
        _logger.warning(
            "Domiciliation is not found to enable auto reconcile payment mode"
        )
        return
    domiciliation.write({"auto_reconcile_same_payment_mode": True})


@openupgrade.migrate()
def migrate(env, version):
    _enable_auto_reconcile_mode(env)
