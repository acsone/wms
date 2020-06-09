# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import api, models
from odoo.osv.expression import AND, FALSE_LEAF


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def _get_so_to_invoice_domain(self):
        domain = super(StockPicking, self)._get_so_to_invoice_domain()
        if domain == FALSE_LEAF:
            return domain
        return AND(
            [domain, [("partner_invoice_id.invoice_grouping", "=", "by_delivery")]]
        )

    @contextmanager
    def _with_so_partner_auto_join(self):
        field = self.env["sale.order"]._fields["partner_id"]
        auto_join = field.auto_join
        try:
            field.auto_join = True
            yield
        finally:
            field.auto_join = auto_join

    @api.multi
    def do_transfer(self):
        with self._with_so_partner_auto_join():
            # The domain is defined with a dot into the left part of leaf.
            # to optimize the query allow to use SQL join to resolve the
            # criteria on the partner_id
            return super(StockPicking, self).do_transfer()
