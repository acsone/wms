from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env.cr.execute(
        "select id from stock_picking where volume is null and state not in ('cancel', 'done')"
    )
    res = env.cr.fetchall()
    pickings = env["stock.picking"].browse([r[0] for r in res])
    pickings.move_ids.product_id._compute_volume()
    pickings.move_ids._compute_volume()
    pickings._compute_volume()
    env.cr.commit()
    env.cr.execute(
        "update stock_picking set volume = 0 where volume is null and state not in ('cancel', 'done')"
    )
    env.cr.commit()
