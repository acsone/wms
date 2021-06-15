# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    def manage_package_type(self):
        res = super(StockPackOperation, self).manage_package_type()
        picking = self.picking_id
        if picking.carrier_id.delivery_type == "gls":
            res = picking._get_gls_put_in_pack_wizard_action(self.result_package_id.id)
        return res
