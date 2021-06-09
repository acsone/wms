# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def put_in_pack(self):
        res = super(StockPicking, self).put_in_pack()
        if res and self.carrier_id.delivery_type == "gls":
            self.gls_send_shipping_package(package=res)
        return res
