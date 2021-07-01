# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _should_check_operator(self):
        is_gls = self.delivery_type == "gls"
        skip_gls = is_gls and self.picking_type_id.code == "outgoing"
        return not skip_gls and super(StockPicking, self)._should_check_operator()
