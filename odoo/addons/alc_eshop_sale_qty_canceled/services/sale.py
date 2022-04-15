# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleService(Component):
    _inherit = "shopinvader.sale.service"

    def _convert_one_line(self, line):
        json = super(SaleService, self)._convert_one_line(line)
        json["qty_canceled"] = line.product_qty_canceled or 0
        return json
