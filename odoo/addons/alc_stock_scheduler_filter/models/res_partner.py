# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.stock.models.res_partner import Partner


class ResPartner(Partner):

    is_manage_day_1 = fields.Boolean("Monday")
    is_manage_day_2 = fields.Boolean("Tuesday")
    is_manage_day_3 = fields.Boolean("Wednesday")
    is_manage_day_4 = fields.Boolean("Thursday")
    is_manage_day_5 = fields.Boolean("Friday")
    is_manage_day_6 = fields.Boolean("Saturday")
    is_manage_day_7 = fields.Boolean("Sunday")
