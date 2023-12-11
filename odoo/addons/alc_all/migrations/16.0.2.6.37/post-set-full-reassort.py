# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Set full reservation for réassorts picking types
    ids = [14, 37, 13]
    picking_types = env["stock.picking.type"].browse(ids)
    picking_types.write(
        {
            "is_full_location_reservation_visible": True,
        }
    )

    # Set full location reservation in shopfloor scenarii
    ids = [9, 15]
    menus = env["shopfloor.menu"].browse(ids)
    menus.write(
        {
            "full_location_reservation": True,
        }
    )
