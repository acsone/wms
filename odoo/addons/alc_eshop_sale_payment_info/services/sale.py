# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleService(Component):
    _inherit = "shopinvader.sale.service"

    def _convert_one_sale(self, sale):
        json = super(SaleService, self)._convert_one_sale(sale)
        json["payment"] = self._convert_payment_to_json(sale)
        return json

    def _convert_payment_to_json(self, sale):
        payment = {"mode": None}
        if sale.payment_mode_id:
            payment["mode"] = {
                "id": sale.payment_mode_id.id,
                "name": sale.payment_mode_id.name,
            }
        return payment
