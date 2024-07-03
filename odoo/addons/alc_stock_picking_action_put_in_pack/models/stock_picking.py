# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def _pre_put_in_pack_hook(self, move_line_ids):
        res = super()._pre_put_in_pack_hook(move_line_ids)
        if not res and self.picking_type_id.set_delivery_package_type_on_put_in_pack:
            return self._set_delivery_package_type()
        return res

    def _set_delivery_package_type(self, batch_pack=False):
        self.ensure_one()
        res = super()._set_delivery_package_type(batch_pack=batch_pack)
        context = res.get("context", self.env.context)
        if (
            not context.get("current_package_carrier_type")
            and self.picking_type_id.set_delivery_package_type_on_put_in_pack
            and not self.carrier_id
            and not self.ship_carrier_id
        ):
            context = dict(context, current_package_carrier_type="none")
        res["context"] = context
        return res
