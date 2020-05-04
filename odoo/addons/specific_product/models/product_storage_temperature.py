# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import fields, models


class StorageTemperatures(models.Model):
    _name = "product.storage.temperature"

    name = fields.Char(required=True)
    temperature = fields.Float(u"Temperature (°C)")
    esb_ref = fields.Char(string="Reference for ESB")
