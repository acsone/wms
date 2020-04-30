# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def unlink(self):
        """ In standard, when a PO line is deleted, the procurement is set in
        exception. If the procurement is related to an orderpoint, then we
        cancel it. This will allow next run of the scheduler to compute a new
        procurement and create a new po line. Note that any quantity in a
        procurement in exception is taken into account in the need computation
        """
        for line in self:
            line.procurement_ids.filtered(
                lambda r: r.orderpoint_id and r.state != 'cancel'
            ).write({'state': 'cancel'})
        return super(PurchaseOrderLine, self).unlink()
