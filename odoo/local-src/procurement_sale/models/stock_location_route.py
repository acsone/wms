# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.addons.procurement.models.procurement import PROCUREMENT_PRIORITIES


class StockLocationRoute(models.Model):
    _inherit = "stock.location.route"

    priority = fields.Selection(PROCUREMENT_PRIORITIES, string='Priority')
