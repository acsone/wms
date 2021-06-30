# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    sale_channel = fields.Selection(
        selection_add=[("placedesvetos", u"Place des Vétos")]
    )

    def _get_b2c_sale_channels(self):
        res = super(SaleOrder, self)._get_b2c_sale_channels()
        res.append("placedesvetos")
        return res
