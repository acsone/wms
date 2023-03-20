# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _xfer_old_user_volume_fields_to_new(env):
    #  get old fields values in a dict with id as key
    query = """
        SELECT id, min_volume_liter, max_volume_liter
        FROM stock_device_type
    """
    env.cr.execute(query)
    old_values = {x[0]: (x[1], x[2]) for x in env.cr.fetchall()}

    # get the liter uom
    liter_uom_id = env.ref("uom.product_uom_litre")

    # loop the stock.device.type to recompute new values from old ones
    for device in env["stock.device.type"].search([]):
        device.user_volume_uom_id = liter_uom_id
        device.user_min_volume, device.user_max_volume = old_values[device.id]


def _remove_columns(env):
    # remove old stored fields min_volume_liter and max_volume_liter
    query = """
        ALTER TABLE stock_device_type
        DROP COLUMN IF EXISTS min_volume_liter,
        DROP COLUMN IF EXISTS max_volume_liter
    """
    env.cr.execute(query)


@openupgrade.migrate()
def migrate(env, version):
    _xfer_old_user_volume_fields_to_new(env)
    _remove_columns(env)
