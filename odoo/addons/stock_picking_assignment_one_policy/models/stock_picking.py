# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _compute_can_assign_operator(self):
        """False for 'all at once' pickings waiting for other pickings.
        For records that have an 'all at once' delivery policy,
        we don't want to be able to start the picking if other picking are still waiting.
        """
        # pylint: disable=missing-return
        super(StockPicking, self)._compute_can_assign_operator()
        records_one = self.filtered(lambda p: p.move_type == "one")
        for record in records_one:
            domain_record = [
                ("group_id", "=", record.group_id.id),
                ("picking_type_code", "=", record.picking_type_code),
                ("state", "not in", ["assigned", "done"]),
            ]
            if self.search_count(domain_record):
                record.can_assign_operator = False
