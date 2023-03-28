# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_users import Users as BaseUsers


class ResUsers(BaseUsers):

    pywebdriver_proxy_ip = fields.Char(
        string="PyWebDriver IP Address",
        size=45,
        help="The hostname or ip address of the hardware proxy",
        required=True,
        default="https://localhost:8069",
    )
