# -*- coding: utf-8 -*-
# Copyright 2018 Sylvain Van Hoof (Okia SPRL)
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.osv import expression


class ProcurementOrder(models.Model):
    _inherit = "procurement.order"

    restrict_lot_id = fields.Many2one(
        "stock.production.lot",
        "Lot/Serial Number",
        help="Technical field used to depict a restriction on the lot/serial "
        "number of quants to consider when marking this move as 'done'",
    )

    def _get_stock_move_values(self):
        res = super(ProcurementOrder, self)._get_stock_move_values()
        res["restrict_lot_id"] = self.restrict_lot_id.id
        return res

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

        location_output = self.env.ref("stock.stock_location_output")
        if self.location_id == location_output:
            product_picking_zone = self.product_id.picking_zone_id
            domain = expression.AND(
                [
                    [("picking_type_id.picking_zone_id", "=", product_picking_zone.id)],
                    domain,
                ]
            )

        return super(ProcurementOrder, self)._search_suitable_rule(domain)
