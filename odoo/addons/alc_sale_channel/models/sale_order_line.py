# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase


class SaleOrderLine(SaleOrderLineBase):

    sale_channel_id = fields.Many2one(
        comodel_name="sale.channel", related="order_id.sale_channel_id", store=True
    )
