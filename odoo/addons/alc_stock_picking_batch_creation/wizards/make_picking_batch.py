# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType
from odoo.addons.stock_picking_batch_creation.wizards import make_picking_batch


class MakePickingBatch(make_picking_batch.MakePickingBatch):

    picking_type_ids = fields.Many2many[PickingType](domain="[('code','=','internal')]")

    def _compute_device_to_use(self, first_picking_to_cluster):
        partner = first_picking_to_cluster.partner_id
        partner_devices = partner._get_specific_stock_devices()
        if partner_devices:
            menu_devices = self.stock_device_type_ids
            for device in partner_devices:
                if device in menu_devices:
                    # Only one device should be put by zone on the partner so creating
                    # a list is useless
                    return device
        return super()._compute_device_to_use(first_picking_to_cluster)
