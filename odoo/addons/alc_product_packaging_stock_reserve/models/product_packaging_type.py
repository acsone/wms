# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductPackagingType(models.Model):

    _inherit = "product.packaging.type"

    stock_reservation_factor = fields.Float(
        "Reservation factor",
        help="Factor specifying what is the acceptable percentage of a "
        "package reservable.",
    )
