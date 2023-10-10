# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    vlb = env.ref("alc_stock_location_data.stock_location_vlb")

    # Change location AX00A0 parent to Parking Aliments
    location_ax00a0 = env.ref("__setup__.stock_location_PA_A")
    if location_ax00a0:
        location_ax00a0.location_id = env.ref(
            "__setup__.stock_location_parking_ali", False
        )

    # Change location Parking Aliments Etagere parent to Parking Aliments
    location_etagere = env["stock.location"].browse(17700)
    if location_etagere:
        location_etagere.location_id = env.ref("__setup__.stock_location_parking_ali")

    # Change all reserve sublocations parent to 'Réserve'
    reserve = env.ref("alc_all.stock_location_reserve")
    reserve_ali = env.ref("__setup__.stock_location_reserve_ali", False)
    if reserve_ali:
        reserve_ali.location_id = env.ref("alc_all.stock_location_reserve")

    reserve_frigo = env["stock.location"].browse(57209)
    if reserve_frigo:
        reserve_frigo.location_id = reserve
    reserve_medoc = env.ref("__setup__.stock_location_reserve_medoc")
    if reserve_medoc:
        reserve_medoc.location_id = reserve

    # Change location to 'VLB' on 'Buy' route
    buy = env.ref("purchase_stock.route_warehouse0_buy")
    buy.rule_ids.location_dest_id = vlb
