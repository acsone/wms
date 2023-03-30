# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    supplier_discount = fields.Float("Supplier discount %")
    is_manage_day_1 = fields.Boolean("Monday")
    is_manage_day_2 = fields.Boolean("Tuesday")
    is_manage_day_3 = fields.Boolean("Wednesday")
    is_manage_day_4 = fields.Boolean("Thursday")
    is_manage_day_5 = fields.Boolean("Friday")
    is_manage_day_6 = fields.Boolean("Saturday")
    is_manage_day_7 = fields.Boolean("Sunday")
