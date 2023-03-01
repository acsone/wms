# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale_channel.models.sale_channel import SaleChannel as SaleChannelBase


class SaleChannel(SaleChannelBase):

    is_internal = fields.Boolean(string="Internal?")
