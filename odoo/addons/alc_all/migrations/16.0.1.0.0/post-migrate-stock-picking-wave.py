# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _stock_picking_wave_state(env):
    query = """
        UPDATE stock_picking_batch
        SET state = 'draft'
        WHERE state = 'released'
    """
    env.cr.execute(query)


def _remove_ir_config_parameter(env):
    query = """
        DELETE FROM ir_config_parameter
        WHERE key like 'constrain_release_picking_wave_before_unlink'
    """
    env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _stock_picking_wave_state(env)
    _remove_ir_config_parameter(env)
