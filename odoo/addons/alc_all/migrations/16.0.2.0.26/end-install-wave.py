from openupgradelib import openupgrade


def _install_wave(env):
    # Ensure wave pickings is available
    env["res.config.settings"].create(
        {"module_stock_picking_batch": True, "group_stock_picking_wave": True}
    ).execute()


@openupgrade.migrate()
def migrate(env, version):
    _install_wave(env)
