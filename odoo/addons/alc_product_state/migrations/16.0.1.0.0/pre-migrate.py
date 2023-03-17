# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _move_product_template(env):
    _logger.info("product.template: move field 'state_id'")
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        ["state_id"],
        "alc_product_state",
        "product_state",
    )


def _move_product_state(env):
    _logger.info("product_state: move field 'name', 'code' and 'sequence'")
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        ["name", "code", "sequence"],
        "alc_product_state",
        "product_state",
    )


def _rename_state_id_in_product_template(env):
    if not openupgrade.column_exists(env.cr, "product_template", "product_state_id"):
        _logger.info("product.template: rename field 'state_id' in 'product_state_id")
        fields = [
            (
                "product.template",
                "product_template",
                "state_id",
                "product_state_id",
            )
        ]
        openupgrade.rename_fields(env, fields)
    else:
        _logger.info("product.template: initialize field 'product_state_id")
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE product_template
            SET product_state_id = state_id
            WHERE state_id IS NOT NULL
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    _move_product_template(env)
    _move_product_state(env)
    _rename_state_id_in_product_template(env)
