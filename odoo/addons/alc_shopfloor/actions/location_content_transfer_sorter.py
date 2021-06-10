# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class LocationContentTransferSorter(Component):

    _name = "shopfloor.location.content.transfer.sorter"
    _inherit = "shopfloor.process.action"
    _usage = "location_content_transfer.sorter"

    def __init__(self, work_context):
        super(LocationContentTransferSorter, self).__init__(work_context)
        self._pickings = self.env["stock.picking"].browse()
        self._content = None

    def feed_pickings(self, pickings):
        self._pickings |= pickings

    def operations(self):
        """Returns valid pack operations

        """
        # lines without package level only (raw products)
        operations = self._pickings.mapped("pack_operation_ids").filtered(
            lambda line: line.state not in ("cancel", "done")
        )
        return operations

    @staticmethod
    def _sort_key(content):
        location_dest_kind_priority = ["reserve", "bin", "parking"]
        # content can be either a move line, either a package
        # level
        location_dest_kind = content.location_dest_id.kind or "bin"
        kind_index = (
            location_dest_kind_priority.index(location_dest_kind)
            if location_dest_kind in location_dest_kind_priority
            else float("inf")
        )
        return (
            # be sure that reserve comes first
            kind_index,
            # postponed content after other contents
            content.shopfloor_priority or 10,
            # sort by shopfloor picking sequence
            content.location_dest_id.shopfloor_picking_sequence or "",
            # sort by similar destination
            content.location_dest_id.complete_name,
            # lines before packages (if we have raw products and packages, raw
            # will be on top? wild guess)
            0 if content.product_id else 1,
            # to have a deterministic sort
            content.id,
        )

    def sort(self):
        self._content = sorted(self.operations(), key=self._sort_key)

    def __iter__(self):
        if self._content is None:
            self.sort()
        return iter(self._content)

    def next(self):
        return next(iter(self))
