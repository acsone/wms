# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.stock_picking_batch_creation.models.stock_device_type import (
    StockDeviceType,
)


class ResPartner(Partner):

    device_type_ids = fields.Many2many[StockDeviceType](
        string="Specific device types",
    )

    def _get_specific_stock_devices(self):
        self.ensure_one()
        return self.device_type_ids or self.parent_id.device_type_ids
