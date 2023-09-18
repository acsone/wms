# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_14_0_2_0_0(env):
    openupgrade.remove_tables_fks(env.cr, ["bank_payment_line"])


@openupgrade.migrate()
def migrate(env, version):
    _migrate_14_0_2_0_0(env)
