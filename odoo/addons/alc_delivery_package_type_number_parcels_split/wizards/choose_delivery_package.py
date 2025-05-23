# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ChooseDeliveryPackage(models.TransientModel):

    _inherit = "choose.delivery.package"

    def action_put_in_pack(self):
        res = None
        package_type = self.delivery_package_type_id
        if (
            package_type.auto_distribute_products_in_parcels
            and package_type.number_of_parcels != 1
        ):
            move_line_ids = self.picking_id._package_move_lines(
                batch_pack=self.env.context.get("batch_pack")
            )
            package_name = self.env["ir.sequence"].next_by_code("stock.quant.package")

            for i, mls in enumerate(
                self.picking_id._distribute_move_lines_in_parcels(
                    move_line_ids, package_type.number_of_parcels
                )
            ):
                default_package_name = package_name + f"_{i+1}"
                self_ctx = self.with_context(
                    forced_lines=mls, default_package_name=default_package_name
                )
                res = super(ChooseDeliveryPackage, self_ctx).action_put_in_pack()

        else:
            res = super().action_put_in_pack()
        return res
