# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    vlb = env.ref("alc_stock_location_data.stock_location_vlb")

    # Change default destination for Reassorts picking types
    medoc = env.ref("alc_shopfloor.stock_picking_type_reassort_medoc", False)
    if medoc:
        medoc.default_location_dest_id = vlb

    frigo = env["stock.picking.type"].browse(37)
    if frigo:
        frigo.default_location_dest_id = vlb

    ali = env.ref("__setup__.stock_picking_type_reassort_ali", False)
    if ali:
        ali.default_location_dest_id = vlb
