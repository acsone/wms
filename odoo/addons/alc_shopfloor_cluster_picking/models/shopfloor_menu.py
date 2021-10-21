# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ShopfloorMenu(models.Model):

    _inherit = "shopfloor.menu"

    batch_create = fields.Boolean(
        string="Automatic Batch Creation",
        default=False,
        help='Automatically create a batch when an operator uses the "Get Work"'
        " button and no existing batch has been found. The system will first look"
        " for priority transfers and fill up the batch till the defined"
        " constraints (max of transfers, volume, weight, ...).",
    )

    stock_device_type_ids = fields.Many2many(
        comodel_name="stock.device.type",
        string="Default device types",
        help="Default list of eligible device types when creating a batch transfer",
    )
    maximum_number_of_preparation_lines = fields.Integer(
        default=20,
        string="Maximum number of preparation lines for the batch",
        required=True,
    )

    @api.constrains("batch_create", "stock_device_type_ids")
    def _check_stock_device_types_ids(self):
        for rec in self.filtered("batch_create"):
            if not rec.stock_device_type_ids:
                raise ValidationError(_("Default device types are required"))
