# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def _prepare_pack_ops(self, quants, forced_qties):
        self.ensure_one()
        new_self = self
        if self.picking_type_id.ignore_putaway_reserve:
            new_self = self.with_context(ignore_putaway_reserve=True)
            fields.copy_cache(self, new_self.env)
        return super(StockPicking, new_self)._prepare_pack_ops(quants, forced_qties)
