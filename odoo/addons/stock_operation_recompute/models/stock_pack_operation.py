# -*- coding: utf-8 -*-
# Copyright 2021 ASCONSE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"

    @api.model
    def _get_fields_to_preserve_recompute_qty(self):
        """
        Return a list a field that must be preserved when pack operations
        are recomputed
        """
        return ["qty_done", "result_package_id"]

    @api.multi
    def _backup_for_recompute(self):
        """
        Return a list of dictionaries with informations to preserve when the
        operation will be recomputed
        """
        res = []
        _fields = self._get_fields_to_preserve_recompute_qty()
        for rec in self:
            values = {}
            for f in _fields:
                val = rec[f]
                if isinstance(val, models.Model):
                    val = val.id
                values[f] = val
            values["lots"] = lots = {}
            for pack_lot in rec.pack_lot_ids:
                lots[pack_lot.lot_id.id] = pack_lot._backup_for_recompute()
            res.append(values)
        return res
