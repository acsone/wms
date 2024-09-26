# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _create_missing_indexes(env):
    """Create missing indexes declared on models.

    This script is useful to ensure after an upgrade of odoo that new
    indexes are created on the database without having to call the
    `update` command on core addons.
    """
    models = list(env)
    env.registry.check_indexes(env.cr, models)


@openupgrade.migrate()
def migrate(env, version):
    _create_missing_indexes(env)
