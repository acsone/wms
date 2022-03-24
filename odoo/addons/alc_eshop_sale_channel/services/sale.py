# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.osv import expression

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class SaleService(Component):
    _inherit = "shopinvader.sale.service"

    def _get_base_search_domain(self):
        domain = super(SaleService, self)._get_base_search_domain()
        return expression.AND(
            [
                domain,
                [
                    (
                        "sale_channel",
                        "in",
                        self.env["sale.order"]._get_sale_channels_internal(),
                    )
                ],
            ]
        )

    def _convert_one_sale(self, sale):
        json = super(SaleService, self)._convert_one_sale(sale)
        json["sale_channel"] = sale.sale_channel
        return json
