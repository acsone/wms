# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    @api.multi
    def _search_suitable_rule(self, domain):
        """
        The MTO route contains several rules (one for each picking zone).
        If the product uses the MTO route, we need to force the picking
        zone.
        :param domain:
        :return:
        """
        self.ensure_one()

        is_output_location = False
        # Location Output
        output_location_id = self.env.ref('stock.stock_location_output').id
        for sub_domain in domain:
            if len(sub_domain) != 3:
                continue
            # Check the domain contains [('location_id', 'in', [1, 2])]
            if sub_domain[0] != 'location_id':
                continue

            if isinstance(sub_domain[2], (tuple, list)):
                is_output_location = output_location_id in sub_domain[2]
            elif isinstance(sub_domain[2], int):
                is_output_location = output_location_id == sub_domain[2]

            if is_output_location:
                break

        if is_output_location:
            product_picking_zone = self.product_id.picking_zone_id
            domain = expression.AND(
                [[('picking_type_id.picking_zone_id', '=',
                   product_picking_zone.id)],
                 domain])

        return super(ProcurementOrder, self)._search_suitable_rule(domain)
