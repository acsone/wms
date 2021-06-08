# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    pywebdriver_proxy_ip = fields.Char(
        string="PyWebDriver IP Address",
        size=45,
        help="The hostname or ip address of the hardware proxy",
        required=True,
        default="http://localhost:8000",
    )
