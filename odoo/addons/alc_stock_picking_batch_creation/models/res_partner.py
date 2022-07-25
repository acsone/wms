# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    device_type_ids = fields.Many2many(
        comodel_name="stock.device.type", string="Specific device types for partner",
    )

    def _get_specific_stock_devices(self):
        self.ensure_one()
        return self.device_type_ids or self.parent_id.device_type_ids
