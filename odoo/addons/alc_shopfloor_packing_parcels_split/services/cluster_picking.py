# Copyright 2025 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.component.core import Component
from odoo.addons.stock.models.stock_quant import QuantPackage


class ClusterPicking(Component):

    _inherit = "shopfloor.cluster.picking"

    def _put_in_pack(
        self, picking, move_lines, number_of_parcels=None, package_type_id=None
    ) -> QuantPackage:
        packages = self.env["stock.quant.package"]
        package_type = self.env["stock.package.type"].browse(package_type_id)
        split_number = number_of_parcels or package_type.number_of_parcels
        if package_type.auto_distribute_products_in_parcels and split_number > 1:
            # in the case of multiple parcels, we need to split the move lines
            # into multiple packages
            package_name = self.env["ir.sequence"].next_by_code("stock.quant.package")
            for i, mls in enumerate(
                picking._distribute_move_lines_in_parcels(
                    move_lines, package_type.number_of_parcels
                )
            ):
                default_package_name = package_name + f"_{i+1}"
                pick_in_ctx = picking.with_context(
                    forced_lines=mls, default_package_name=default_package_name
                )
                packages |= super()._put_in_pack(
                    pick_in_ctx, mls, None, package_type.id
                )
        else:
            packages = super()._put_in_pack(
                picking, move_lines, number_of_parcels, package_type_id
            )
        return packages
