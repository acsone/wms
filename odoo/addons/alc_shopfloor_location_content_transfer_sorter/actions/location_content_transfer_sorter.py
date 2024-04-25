# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class LocationContentTransferSorter(Component):

    _inherit = "shopfloor.location.content.transfer.sorter"

    @staticmethod
    def _sort_key(content):
        # content can be either a move line, either a package
        # level
        return (
            # postponed content after other contents
            content.shopfloor_priority or 10,
            # sort by shopfloor picking sequence
            content.location_dest_id.shopfloor_picking_sequence or "",
            # sort by similar destination
            content.location_dest_id.name,
            # lines before packages (if we have raw products and packages, raw
            # will be on top? wild guess)
            0 if content._name == "stock.move.line" else 1,
            # to have a deterministic sort
            content.id,
        )
