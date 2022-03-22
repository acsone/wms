# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    @api.model
    def _get_sale_channels_external_selection(self):
        res = super(SaleOrder, self)._get_sale_channels_external_selection()
        res.append(("clubvetshop", "ClubVetShop"))
        return res
