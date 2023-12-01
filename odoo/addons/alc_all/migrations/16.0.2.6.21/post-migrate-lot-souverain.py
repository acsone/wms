# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Cancel all waiting outgoing moves for colis souverain that haven't
    # an internal quantity.
    move_obj = env["stock.move"]

    # Colis Souverain / Frigo / Immuno
    for product_id in [32669, 41049, 36581]:
        moves_out = move_obj.search(
            [
                ("product_id", "=", product_id),
                ("state", "=", "waiting"),
                ("location_dest_id.usage", "=", "customer"),
            ]
        )
        colis_quant = env["stock.quant"].search(
            [("product_id", "=", product_id), ("location_id.usage", "=", "internal")]
        )
        # Check that the move is not waiting a quantity that still exists in stock
        moves = moves_out.filtered(
            lambda m, colis_quant=colis_quant: m.restrict_lot_id.name
            not in colis_quant.mapped("lot_id.name")
        )
        moves._action_cancel()
