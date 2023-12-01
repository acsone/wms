# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def set_destination_all(self, picking_batch_id, barcode, confirmation=False):
        """
        Ignore dynamic routing in cluster picking scenario when.

        validation the batch, at this stage the location_dest is already set
        """
        self.env.context = dict(exclude_apply_dynamic_routing=True, **self.env.context)
        return super().set_destination_all(
            picking_batch_id, barcode, confirmation=confirmation
        )
