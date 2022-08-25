# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementOrder(models.Model):

    _inherit = "procurement.order"
    do_not_deliver_line = fields.Boolean(defaut=False)

    def _get_stock_move_values(self):
        res = super(ProcurementOrder, self)._get_stock_move_values()
        res["do_not_deliver_line"] = self.do_not_deliver_line
        return res
