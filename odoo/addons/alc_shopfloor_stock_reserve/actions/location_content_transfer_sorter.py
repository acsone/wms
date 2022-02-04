# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class LocationContentTransferSorter(Component):

    _inherit = "shopfloor.location.content.transfer.sorter"

    def _sort_key(self, content):
        sorter_keys = super(LocationContentTransferSorter, self)._sort_key(content)
        location_dest_kind_priority = ["reserve", "bin", "parking"]
        # content can be either a move line, either a package
        # level
        location_dest_kind = content.location_dest_id.kind or "bin"
        kind_index = (
            location_dest_kind_priority.index(location_dest_kind)
            if location_dest_kind in location_dest_kind_priority
            else float("inf")
        )
        # be sure that reserve comes first
        sorter_keys = (kind_index,) + sorter_keys
        return sorter_keys
