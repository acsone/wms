# -*- coding: utf-8 -*-
# © 2017 Sylvain Van Hoof
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models, api

from .. import constants


class ReportStockQuantBylocation(models.Model):
    _inherit = 'report.stock.quant.bylocation'

    @api.multi
    def create_parking_picking(self):
        picking = super(ReportStockQuantBylocation, self)\
            .create_parking_picking()

        picking.write({
            'zetes_picking_type': constants.PARKING_ASSIGNMENT
        })

        return picking


class ReportStockQuantBylocationReserve(models.Model):
    _inherit = 'report.stock.quant.bylocation.reserve'

    @api.multi
    def create_reserve_picking(self):
        picking = super(ReportStockQuantBylocationReserve, self)\
            .create_reserve_picking()

        picking.write({
            'zetes_picking_type': constants.RESERVE_ASSIGNMENT
        })

        return picking
