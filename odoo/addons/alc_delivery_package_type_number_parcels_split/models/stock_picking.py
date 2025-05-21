# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


def split_recordset(rs, n):
    """
    Split an Odoo recordset `rs` into `n` recordsets with balanced sizes.

    Returns a list of `n` recordsets.
    """
    total = len(rs)
    base_size = total // n
    remainder = total % n

    result = []
    start = 0
    for i in range(n):
        size = base_size + (1 if i < remainder else 0)
        result.append(rs[start : start + size])
        start += size

    return result


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _distribute_move_lines_in_parcels(self, move_line_ids, nbr_packs=1):
        """Distribute the move lines in the parcels.

        Contraints:
        - The number of parcels must be greater than 0.
        - The number of items to pack must be greater or equal to the number of parcels.

        If the number of move lines is less than the number of parcels we must
        split the move lines to distribute them in the parcels.

        :param move_line_ids: list of move line ids to distribute
        :param nbr_packs: number of packs to create
        :return: a list of recordsset of move lines
        """
        move_line_ids = move_line_ids.filtered(
            lambda ml: float_compare(
                ml.qty_done, 0.0, precision_rounding=ml.product_uom_id.rounding
            )
            > 0
        )
        if nbr_packs <= 0:
            raise ValidationError(_("The number of parcels must be greater than 0."))
        if sum(move_line_ids.mapped("qty_done")) < nbr_packs:
            raise ValidationError(
                _(
                    "The number of items to pack must be greater or equal to the number of parcels."
                )
            )
        if len(move_line_ids) >= nbr_packs:
            # we return a list of lines distributed in the parcels
            return split_recordset(move_line_ids, nbr_packs)

        # from here we have less move lines than parcels
        # 1. Assign the undivisible move lines to the parcels
        chunks = []
        unassigned_lines = []
        for ml in move_line_ids:
            # pylint: disable=use-implicit-booleaness-not-comparison-to-zero
            if (
                float_compare(
                    ml.qty_done, 1, precision_rounding=ml.product_uom_id.rounding
                )
                == 0
            ):
                # we can assign the move line to a parcel
                chunks.append(ml)
            else:
                # we cannot assign the move line to a parcel
                unassigned_lines.append(ml)
        remaining_parcels = nbr_packs - len(chunks)
        # 2. We order the unassigned move lines by qty_done
        unassigned_lines = sorted(unassigned_lines, key=lambda ml: ml.qty_done)
        while remaining_parcels > 1:
            # we take the first move line, split it to take 1 unit and assign it to a parcel
            # and put the rest in the unassigned lines
            ml = unassigned_lines[0]
            qty_done = ml.qty_done
            if (
                float_compare(
                    qty_done, 1, precision_rounding=ml.product_uom_id.rounding
                )
                > 0
            ):
                # we can assign the move line to a parcel
                new_ml = ml.copy({"qty_done": 1, "reserved_uom_qty": 1})
                ml.write(
                    {
                        "qty_done": ml.qty_done - 1,
                        "reserved_uom_qty": ml.reserved_uom_qty - 1,
                    }
                )
                chunks.append(new_ml)
            else:
                chunks.append(ml)
                unassigned_lines.pop(0)
            remaining_parcels -= 1
        # add the remaining unassigned lines to the last parcel
        chunks.append(
            self.env["stock.move.line"].browse([i.id for i in unassigned_lines])
        )
        return chunks

    def _package_move_lines(self, batch_pack=False):
        if "forced_lines" in self.env.context:
            return self.env.context["forced_lines"]
        return super()._package_move_lines(batch_pack=batch_pack)
