# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


# Change order to ensure that first sold, is first served
class ProcurementOrder(models.Model):
    _inherit = "procurement.order"
    _order = "priority desc, id asc"
