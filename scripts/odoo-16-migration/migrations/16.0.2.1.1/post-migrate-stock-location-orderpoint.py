# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo.fields import Command

_logger = logging.getLogger(__name__)


def _migrate_reserves(env):
    orderpoint_obj = env["stock.location.orderpoint"]
    location_obj = env["stock.location"]
    query = """
        SELECT id, x_reserve_location_id
            FROM stock_location
                WHERE x_reserve_location_id IS NOT NULL
                AND NOT EXISTS (SELECT 1 FROM stock_location_orderpoint WHERE location_id = stock_location.id)
    """

    env.cr.execute(query)
    results = env.cr.fetchall()

    # Create first the route
    route = env["stock.route"].create(
        {
            "name": "Reassort",
            "warehouse_selectable": True,
            "warehouse_ids": [Command.set(env.ref("stock.warehouse0").ids)],
            "sequence": 999,
        }
    )

    # Create the picking type (Can be changed after on stock rules)
    picking_type = env["stock.picking.type"].create(
        {
            "name": "Reassort",
            "sequence_code": "REASS",
            "code": "internal",
            "show_operations": True,
            "show_reserved": True,
        }
    )

    rule_obj = env["stock.rule"]
    # Creating a rule per tuple (location , source_location) will
    # allow to compute correctly the source location for the orderpoint
    # using just one route for all the reassorts.
    for result in results:
        dest = location_obj.browse(result[0])
        src = location_obj.browse(result[1])
        rule = rule_obj.create(
            {
                "name": "Reassort %(src_name)s => %(dest_name)s"
                % {"src_name": src.name, "dest_name": dest.name},
                "route_id": route.id,
                "action": "pull",
                "location_dest_id": dest.id,
                "location_src_id": src.id,
                "procure_method": "make_to_stock",
                "picking_type_id": picking_type.id,
            }
        )
        _logger.info(
            "Creating Reassort stock rule %(rule_name)s", {"rule_name": rule.name}
        )
        orderpoint_obj.create(
            {
                "route_id": route.id,
                "location_id": result[0],
            }
        )


@openupgrade.migrate()
def migrate(env, version):
    _migrate_reserves(env)
