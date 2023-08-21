from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    scenario = env.ref("shopfloor.scenario_location_content_transfer")
    menus = env["shopfloor.menu"].search([("scenario_id", "=", scenario.id)])
    menus.write({"allow_get_work": True, "allow_move_create": False})
