# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api

from odoo.addons.alc_b2c_connector.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):
    @api.model
    def _parse_b2c_order(self, data, endpoint_setting):
        res = super()._parse_b2c_order(data, endpoint_setting)
        res["discount_pricelist_ids"] = [
            Command.set(endpoint_setting.discount_pricelist_id.ids)
        ]
        return res
