# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductStorageTemperature(models.Model):

    _name = "product.storage.temperature"
    _description = "Storage Temperature"

    name = fields.Char(required=True, translate=True)
    temperature = fields.Float("Temperature (°C)")
