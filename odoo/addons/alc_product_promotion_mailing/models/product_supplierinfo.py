# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductSupplierinfo(models.Model):

    _inherit = "product.supplierinfo"

    reminder_mailing_sent = fields.Boolean()
