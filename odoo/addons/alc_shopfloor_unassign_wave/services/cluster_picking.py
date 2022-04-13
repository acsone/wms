# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def _cancel_batch(self, picking_batch_id):
        batch = super(ClusterPicking, self)._cancel_batch(picking_batch_id)
        if batch.exists():
            batch.release()
        return batch
