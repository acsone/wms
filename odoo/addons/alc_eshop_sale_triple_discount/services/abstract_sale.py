# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_line_unit_price(self, line):
        value = super(AbstractSaleService, self)._convert_one_line_unit_price(line)
        value["untaxed_with_discount"] = (
            line.price_unit - line.price_unit * (line._get_final_discount() or 0) / 100
        )
        return value

    def _convert_one_line(self, line):
        info = super(AbstractSaleService, self)._convert_one_line(line)
        info["discount"]["rate"] = line._get_final_discount()
        return info
