# -*- coding: utf-8 -*-
# Copyright 2016-2019 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    subcode = fields.Char("Code")


class StockPicking(models.Model):
    _inherit = "stock.picking"

    picking_type_subcode = fields.Char(
        related="picking_type_id.subcode", readonly=True, store=True, index=True
    )


class StockMove(models.Model):
    _inherit = "stock.move"

    picking_type_subcode = fields.Char(related="picking_type_id.subcode", readonly=True)
