# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    # Change location AX00A0 parent to Parking Aliments
    location_ax00a0 = env.ref("__setup__.stock_location_PA_A")
    if location_ax00a0:
        location_ax00a0.location_id = env.ref("__setup__.stock_location_parking_ali")

    # Change location Parking Aliments Etagere parent to Parking Aliments
    location_etagere = env["stock.location"].browse(17700)
    if location_etagere:
        location_etagere.location_id = env.ref("__setup__.stock_location_parking_ali")
