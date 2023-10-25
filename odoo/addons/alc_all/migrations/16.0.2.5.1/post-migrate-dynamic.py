# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.fields import Command


@openupgrade.migrate()
def migrate(env, version):
    routing_obj = env["stock.routing"]
    # Set new dynamic rules
    picking_type = env.ref("alc_all.stock_picking_type_reassort")
    picking_type_aliments = env.ref("__setup__.stock_picking_type_reassort_ali")
    picking_type_frigo = env["stock.picking.type"].browse(37)
    picking_type_medoc = env["stock.picking.type"].browse(13)
    reserve_ali = env.ref("__setup__.stock_location_reserve_ali")
    reserve_frigo = env["stock.location"].browse(57209)
    reserve_medoc = env.ref("__setup__.stock_location_reserve_medoc")
    # Check if they don't exist to avoid duplicate integrity error

    # Aliments
    routing_aliments = routing_obj.search([("location_id", "=", reserve_ali.id)])
    if not routing_aliments:
        routing_obj.create(
            {
                "location_id": reserve_ali.id,
                "picking_type_id": picking_type.id,
                "rule_ids": [
                    Command.create(
                        {
                            "method": "pull",
                            "picking_type_id": picking_type_aliments.id,
                            "location_src_id": reserve_ali.id,
                            "location_dest_id": env.ref(
                                "alc_stock_location_data.stock_location_vlb"
                            ).id,
                        }
                    )
                ],
            }
        )

    # Frigo
    routing_frigo = routing_obj.search([("location_id", "=", reserve_frigo.id)])
    if not routing_frigo:
        routing_obj.create(
            {
                "location_id": reserve_frigo.id,
                "picking_type_id": picking_type.id,
                "rule_ids": [
                    Command.create(
                        {
                            "method": "pull",
                            "picking_type_id": picking_type_frigo.id,
                            "location_src_id": reserve_frigo.id,
                            "location_dest_id": env.ref(
                                "alc_stock_location_data.stock_location_vlb"
                            ).id,
                        }
                    )
                ],
            }
        )

    # Médicaments
    routing_medoc = routing_obj.search([("location_id", "=", reserve_medoc.id)])
    if not routing_medoc:
        routing_obj.create(
            {
                "location_id": reserve_medoc.id,
                "picking_type_id": picking_type.id,
                "rule_ids": [
                    Command.create(
                        {
                            "method": "pull",
                            "picking_type_id": picking_type_medoc.id,
                            "location_src_id": reserve_medoc.id,
                            "location_dest_id": env.ref(
                                "alc_stock_location_data.stock_location_vlb"
                            ).id,
                        }
                    )
                ],
            }
        )
