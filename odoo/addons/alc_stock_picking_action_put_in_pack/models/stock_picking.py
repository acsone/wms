# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):
    def _pre_put_in_pack_hook(self, move_line_ids):
        res = super()._pre_put_in_pack_hook(move_line_ids)
        if (
            not res
            and len(move_line_ids) == 1
            and all(
                move_line_ids.picking_type_id.mapped(
                    "package_type_required_on_put_in_pack"
                )
            )
        ):
            view_id = self.env.ref("stock.stock_package_destination_form_view").id
            wiz = self.env["stock.package.destination"].create(
                {
                    "picking_id": self.id,
                    "location_dest_id": move_line_ids.location_dest_id.id,
                }
            )
            return {
                "name": _("Choose destination location"),
                "view_mode": "form",
                "res_model": "stock.package.destination",
                "view_id": view_id,
                "views": [(view_id, "form")],
                "type": "ir.actions.act_window",
                "res_id": wiz.id,
                "target": "new",
            }
        return res
