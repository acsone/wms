# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    stock_release_channel_id = fields.Many2one(
        comodel_name="stock.release.channel",
        string="Release Channel",
        help="You can choose a dedicated release channel for this partner. All of their"
        " transfers will be assigned to the selected channel, regardless of the "
        "automatic assigning process.",
    )
