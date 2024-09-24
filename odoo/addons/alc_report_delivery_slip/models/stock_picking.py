# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from collections import defaultdict

from odoo import _, api, fields
from odoo.fields import first

from odoo.addons.alc_stock_picking_parcels_and_items_per_source.models.stock_picking import (
    StockPicking as Picking,
)
from odoo.addons.stock_package_type_category.models.stock_package_type_category import (
    StockPackageTypeCategory as PackageTypeCategoryBase,
)


class StockPicking(Picking):

    parcels_and_items_category_ids = fields.Many2many[PackageTypeCategoryBase](
        compute="_compute_parcels_and_items_category_ids",
    )
    parcels_and_items_per_category = fields.Json(
        compute="_compute_parcels_and_items_per_category",
    )

    @api.depends("move_ids")
    def _compute_parcels_and_items_category_ids(self):
        """This will compute the categories to display as headers."""
        category_obj = self.env["stock.package.type.category"]
        categories = category_obj.search(
            [("show_in_delivery_slip_report", "=", True)]
        ).sorted("sequence_in_delivery_slip_report")
        self.parcels_and_items_category_ids = categories

    def get_numbers_per_source(self):
        """
        Return 1 dic from parcels_and_items_per_source field:

            summary = {<source_name>: {'parcels': nbr, 'items': nbr}, ...}
        """
        self.ensure_one()
        summary = {}
        for loc_id in self.parcels_and_items_per_source["locations"]:
            #  loc_id is a str in json field
            loc_id = loc_id.lower()  # because mix of 'False' and 'false' in json
            nb_parcels = self.parcels_and_items_per_source["parcels"].get(loc_id, 0)
            nb_items = self.parcels_and_items_per_source["items"].get(loc_id, 0)
            loc_name = (
                self.env["stock.location"].browse(int(loc_id)).name
                if loc_id.isdecimal()
                else _("Other")
            )
            summary[loc_name] = {"parcels": int(nb_parcels), "items": int(nb_items)}
        return summary

    @api.depends("package_level_ids_details")
    def _compute_parcels_and_items_per_category(self):
        for picking in self:
            all_categories = picking.parcels_and_items_category_ids
            total_location_parcels = defaultdict(int)
            total_quantities = defaultdict(int)  # Total of products without package
            total_parcels = 0
            total_quantity = 0.0
            categories = set()

            for category_id, levels in (
                picking.package_level_ids_details.filtered(
                    lambda level: not level.package_id.is_internal
                )
                .partition(lambda level: level.package_id.package_type_id.category_id)
                .items()
            ):
                value = sum(level.package_id.number_of_parcels for level in levels)
                total_location_parcels[category_id.id] += sum(
                    level.package_id.number_of_parcels for level in levels
                )
                total_parcels += value
                categories.update([category_id.id])
            for category_id, levels in (
                picking.package_level_ids_details.filtered("package_id.is_internal")
                .partition(lambda level: level.package_id.package_type_id.category_id)
                .items()
            ):
                value = sum(quant.quantity for quant in levels.package_id.quant_ids)
                total_quantities[category_id.id] += value
                total_quantity += value
                categories.update([category_id.id])

            # Try to fallback on location origin
            # TODO: Should this be removed ? But: we need to indicate the quantity even if no package...
            for move in picking.move_ids_without_package.filtered(
                lambda move: move.state != "cancel"
            ):
                quantity = move.reserved_availability or move.quantity_done or 0.0
                category = (
                    all_categories.filtered(
                        lambda category, move=move: first(
                            move.source_zone_location_ids
                        ).name
                        == category.name
                    ).id
                    or False
                )
                total_quantities[category] += quantity
                total_quantity += quantity
                categories.update([category])

            picking.parcels_and_items_per_category = {
                "parcels": total_location_parcels,
                "items": total_quantities,
                "parcels_total": total_parcels,
                "items_total": total_quantity,
                "categories": list(categories),
            }
