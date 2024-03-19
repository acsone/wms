# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock_picking_delivery_link.models.stock_picking import (
    StockPicking as Picking,
)


class StockPicking(Picking):
    def _set_delivery_package_type(self):
        """
        As we want to filter package types on carrier even on internal.

        pickings, we pass the delivery type to the context from
        the related carrier taken from the delivery picking.
        """
        self.ensure_one()
        res = super()._set_delivery_package_type()
        context = res.get("context", {})
        if self.picking_type_id.delivery_package_type_none_on_put_in_pack:
            context = dict(context, current_package_carrier_type="none")
        res["context"] = context
        return res
