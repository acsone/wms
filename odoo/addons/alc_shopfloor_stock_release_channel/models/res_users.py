# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.base.models import res_users


class ResUsers(res_users.Users):

    only_one_release_channel_by_picking_batch = fields.Boolean(
        string="Create cluster pickings by release channel for this operator",
        default=True,
    )
