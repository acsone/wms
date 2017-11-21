# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models, api

from .. import constants


class ReportStockQuantBylocation(models.Model):
    _inherit = 'report.stock.quant.bylocation'

    @api.multi
    def create_picking(self):
        picking = super(ReportStockQuantBylocation, self).create_picking()

        if picking.location_id.kind == 'parking':
            picking.zetes_picking_type = constants.PARKING_ASSIGNMENT
        elif picking.location_id.kind == 'reserve':
            picking.zetes_picking_type = constants.RESERVE_ASSIGNMENT

        return picking
