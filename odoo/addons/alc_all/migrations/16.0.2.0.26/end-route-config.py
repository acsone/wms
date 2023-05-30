from openupgradelib import openupgrade


def _configure_route(env):
    # Set release channel behavior for delivery route
    route = env["stock.route"].browse(3)
    route.write(
        {
            "available_to_promise_defer_pull": True,
            "no_backorder_at_release": True,
        }
    )
    route.rule_ids.filtered(
        lambda rule: rule.location_dest_id.usage == "customer"
    ).write({"propagate_carrier": True})


@openupgrade.migrate()
def migrate(env, version):
    _configure_route(env)
