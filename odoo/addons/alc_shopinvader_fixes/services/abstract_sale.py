# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        res = super(AbstractSaleService, self)._convert_one_sale(sale)
        res.update(
            {
                "date": utils.odoo_str_dt_to_dt_utc(sale.date_order),
                "note": sale.note or None,
                "customer_ref": sale.client_order_ref or None,
            }
        )
        return res
