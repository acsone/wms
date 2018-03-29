# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models
from odoo.osv import expression


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _search_suitable_rule(self, domain):
        """
        The MTO route contains several rules (one for each picking zone).
        If the product uses the MTO route, we need to force the picking
        zone.
        :param domain: list - Odoo Domain (eg: [('location_id', 'in', [1, 2])])
        :return:
        """
        self.ensure_one()

        location_output = self.env.ref('stock.stock_location_output')
        if self.location_id == location_output:
            product_picking_zone = self.product_id.picking_zone_id
            domain = expression.AND(
                [[('picking_type_id.picking_zone_id', '=',
                   product_picking_zone.id)],
                 domain])

        return super(ProcurementOrder, self)._search_suitable_rule(domain)
