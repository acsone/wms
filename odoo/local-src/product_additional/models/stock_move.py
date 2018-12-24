# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def do_unreserve(self):
        # picking do_unreserve first unlink pack operations and then calls
        # do_unreserve on moves. As we also unlink additional moves, we need to
        # rebuild the record set otherwise it will complain for missing records
        # in the recordset
        if self.ids:
            self = self.search([('id', 'in', self.ids)])
        return super(StockMove, self).do_unreserve()

    def check_move_lots(self):
        # Called in mrp module just after action_assign
        # As recordset changed, we need to rebuild it otherwise it
        # will complain for missing records in the recordset
        if self.ids:
            self = self.search([('id', 'in', self.ids)])
        return super(StockMove, self).check_move_lots()
