# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AuthApiKey(models.Model):

    _inherit = "auth.api.key"

    shopfloor_user_id = fields.Many2one(
        comodel_name="res.users",
        string="Shopfloor User",
        required=True,
        help="""The user operating the shopfloor app. All the operations are done
        by using the linked user. Nevertheless, to keep a trace af the real user
        operating the mobile app without the use of a real Odoo user, you can
        reference here a portal user that will be linked to the operations done.""",
    )
