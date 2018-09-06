# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _run(self):
        """ On import of sale orders, deactivate MTO + 'buy' procurement rule

        If a sale order has a product with MTO and buy routes it would
        create a PO. In case of sale order import we don't want that PO
        to be generated from there as we also import POs.

        To do so we skip the 'buy' action by replacing it by a 'move' action.

        """
        skipped_rule = None
        if self.env.context.get('__import_no_po_from_so_with_mto'):
            if self.rule_id and self.rule_id.action == 'buy':
                skipped_rule = True
                self.rule_id.action = 'move'
        res = super(ProcurementOrder, self)._run()
        if skipped_rule:
            self.rule_id.action = 'buy'
        return res
