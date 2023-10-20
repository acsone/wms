# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    picking_types = env["stock.picking.type"].browse([16, 15, 24])
    picking_types.write({"show_serial_number": True})
