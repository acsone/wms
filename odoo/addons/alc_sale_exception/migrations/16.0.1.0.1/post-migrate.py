# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from openupgradelib import openupgrade

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def _remove_exceptions_rule_fields(env):
    _logger.info("remove obsolete fields from exception_rule")
    obsolete_fields = ("warning_only", "warning_text")
    for field in obsolete_fields:
        if sql.column_exists(env.cr, "exception_rule", field):
            query = f"ALTER TABLE exception_rule DROP COLUMN IF EXISTS {field}"
            env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _remove_exceptions_rule_fields(env)
