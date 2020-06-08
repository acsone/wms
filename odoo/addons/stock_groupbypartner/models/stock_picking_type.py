# -*- coding: utf-8 -*-
# Copyright 2016-2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019-2020 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    groupbypartner = fields.Boolean("Use existing picking having same partner")
    groupbypartner_maxweight = fields.Integer("Max Weight")
