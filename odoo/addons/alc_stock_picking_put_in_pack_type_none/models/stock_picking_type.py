# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock_picking_delivery_link.models.stock_picking_type import (
    StockPickingType as PickingType,
)


class StockPickingType(PickingType):

    delivery_package_type_none_on_put_in_pack = fields.Boolean(
        compute="_compute_delivery_package_type_none_on_put_in_pack",
        store=True,
        readonly=False,
        help="Check this box if you want to be able to select package types with"
        " no carrier integration in a picking with a shipping carrier defined other"
        " than 'fixed' or 'based on rules' in 'Put in Pack' operation.",
    )

    @api.depends("set_delivery_package_type_on_put_in_pack")
    def _compute_delivery_package_type_none_on_put_in_pack(self) -> None:
        for picking_type in self:
            if not picking_type.set_delivery_package_type_on_put_in_pack:
                picking_type.delivery_package_type_none_on_put_in_pack = False
