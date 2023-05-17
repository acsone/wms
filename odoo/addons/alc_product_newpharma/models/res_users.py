# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models.res_users import Users as UsersBase


class Users(UsersBase):
    is_for_newpharma = fields.Boolean("For NewPharma")
