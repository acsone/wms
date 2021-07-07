# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _get_put_in_pack_package(self, operations):
        package = self.env["stock.quant.package"]
        if self.picking_type_code == "outgoing" and self.delivery_type == "gls":
            package = self._get_gls_pack_package(operations)
        return package or super(StockPicking, self)._get_put_in_pack_package(operations)
