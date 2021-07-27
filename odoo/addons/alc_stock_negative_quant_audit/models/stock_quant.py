# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import StringIO
import traceback

from odoo import api, models


class StockQuant(models.Model):

    _inherit = "stock.quant"

    @api.multi
    def _log_negative_quant(self):
        records = self.filtered(lambda r: r.qty < 0)
        if records:
            stack = StringIO.StringIO()
            traceback.print_stack(file=stack)
            stack.seek(0)
            trace = stack.getvalue()
            for rec in records:
                self.env["stock.negative.quant.audit"].sudo().create(
                    {
                        "quant_id": rec.id,
                        "stacktrace": trace,
                        "user_id": self.env.user.id,
                    }
                )

    @api.model
    def create(self, vals):
        is_negative = vals.get("qyt", 1)
        res = super(StockQuant, self).create(vals)
        if is_negative:
            res._log_negative_quant()
        return res

    def write(self, vals):
        is_negative = vals.get("qyt", 1)
        res = super(StockQuant, self).write(vals)
        if is_negative:
            self._log_negative_quant()
        return res
