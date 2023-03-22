# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import typing

from odoo import fields

from odoo.addons.sale.models.sale_order_line import SaleOrderLine as SaleOrderLineBase

if typing.TYPE_CHECKING:
    pass


class SaleOrderLine(SaleOrderLineBase):

    sale_channel_id = fields.Many2one["SaleChannel"](
        related="order_id.sale_channel_id", store=True
    )
