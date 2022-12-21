# -*- coding: utf-8 -*-
# Copyright 2016-2017 Jacques-Etienne Baudoux (BCIM)
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"
