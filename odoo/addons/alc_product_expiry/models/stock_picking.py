# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):

    to_process_quant_expired = fields.Boolean(
        "Bypass restriction on expired quants",
        inverse="_inverse_to_process_quant_expired",
        tracking=True,
    )

    def _inverse_to_process_quant_expired(self):
        """Make sure the bypass is propagated between related picking."""
        for rec in self:
            new_value = rec.to_process_quant_expired
            pickings = (
                rec.move_ids.move_orig_ids | rec.move_ids.move_dest_ids
            ).picking_id
            pickings = pickings.filtered(lambda p: p.state not in ("cancel", "done"))
            pickings = pickings.filtered(
                lambda p, nv=new_value: p.to_process_quant_expired != nv
            )
            pickings.to_process_quant_expired = rec.to_process_quant_expired
