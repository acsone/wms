# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.sale_stock.models.sale_order import SaleOrder as SaleOrderBase


class SaleOrder(SaleOrderBase):

    do_not_deliver_if_alone = fields.Boolean(default=False)
