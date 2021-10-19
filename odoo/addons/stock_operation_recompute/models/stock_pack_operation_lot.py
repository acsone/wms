# -*- coding: utf-8 -*-
# Copyright 2021 ASCONSE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"

    @api.model
    def _get_fields_to_preserve_recompute_qty(self):
        """
        Return a list a field that must be preserved when pack operations
        are recomputed
        """
        return ["qty"]

    @api.multi
    def _backup_for_recompute(self):
        """
        Return a list of dictionaries with informations to preserve when the
        operation will be recomputed
        """
        self.ensure_one()
        _fields = self._get_fields_to_preserve_recompute_qty()
        values = {}
        for f in _fields:
            val = self[f]
            if isinstance(val, models.Model):
                val = val.id
            values[f] = val
        return values
