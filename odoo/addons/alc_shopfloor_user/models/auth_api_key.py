# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.auth_api_key.models.auth_api_key import AuthApiKey as AuthApiKeyBase
from odoo.addons.base.models.res_users import Users


class AuthApiKey(AuthApiKeyBase):

    shopfloor_user_id = fields.Many2one[Users](
        string="Shopfloor User",
        required=False,
        help="""The user operating the shopfloor app. All the operations are done
        by using the linked user. Nevertheless, to keep a trace af the real user
        operating the mobile app without the use of a real Odoo user, you can
        reference here a portal user that will be linked to the operations done.""",
    )
