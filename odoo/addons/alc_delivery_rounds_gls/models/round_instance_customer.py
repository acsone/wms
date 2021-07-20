# -*- coding: utf-8 -*-
# Copyright 2021 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class RoundInstanceCustomer(models.Model):
    _inherit = "round.instance.customer"

    def button_deliver(self):
        """Do not call _deliver on GLS pickings, operation has to be manual."""
        if not self.delivered and "gls" in self.mapped("picking_ids.delivery_type"):
            window_action = self.env.ref("stock.action_picking_tree_all").read()[0]
            window_action["domain"] = [("id", "in", self.picking_ids.ids)]
            return window_action
        return super(RoundInstanceCustomer, self).button_deliver()
