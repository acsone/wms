# Copyright 2020 ACSONE SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields

from odoo.addons.stock.models.stock_picking import PickingType


class StockPickingType(PickingType):

    # avoid_shipping_cost is used to avoid computing shipping cost for
    # outgoing picking type. It has no effect on other picking types.
    avoid_shipping_cost = fields.Boolean(
        string="Avoid shipping cost",
        default=False,
        help="If selected, the shipping cost will not be added to the sale" "order.",
    )
