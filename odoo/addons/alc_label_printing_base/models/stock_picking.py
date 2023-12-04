# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields
from odoo.exceptions import UserError

from odoo.addons.alc_printing_base.utils import hw_print
from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    checksum = fields.Char("Checksum", copy=False)
    printed_once = fields.Boolean(
        default=False,
        help="Technical field to see if labels for food products in case of "
        "wholesaler have already been printed once since we only need one label",
    )

    def print_packages_label(self, quantity=1, printer_id=False, packages=None):
        self.ensure_one()
        packages = packages or self.mapped("move_line_ids.result_package_id")
        if not packages:
            raise UserError(_("No package in this picking"))
        if not self.partner_id:
            raise Warning(_("No destination partner defined"))
        hw_print(
            self,
            "alc_label_printing_base.report_stock_pick_packs_label",
            printer_id=printer_id,
            qty=quantity,  # not affected by number_labels_to_print
            packages_only=packages,
        )

    def _get_all_dest_pickings(self):
        """
        TODO.

        This method was in delivery_rounds/picking in V10 so it may need to be moved
        somewhere else
        """

        def _descend_moves(lvl):
            next_lvl = lvl.mapped("move_dest_ids")
            if next_lvl:
                lvl |= _descend_moves(next_lvl)
            return lvl

        moves = _descend_moves(self.mapped("move_ids"))
        return moves.mapped("picking_id")
