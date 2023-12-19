# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.stock.models.stock_picking import Picking


class StockPicking(Picking):

    parcels_and_items_per_source = fields.Json(
        compute="_compute_parcels_and_items_per_source",
    )

    @api.depends("move_ids.source_zone_location_ids")
    def _compute_parcels_and_items_per_source(self):
        for picking in self:
            total_location_parcels = {}
            total_quantities = {}  # Total of products without package
            total_parcels = 0
            total_quantity = 0.0
            locations = []
            for location, moves in picking.move_ids.partition(
                "source_zone_location_ids"
            ).items():
                # Workaround for the case mixed products (e.g.: Matériel and Médicaments)
                # have been put in the same package in the same picking.
                # TODO: Decide how to display this in the report.
                if len(location) > 1:
                    # Unknown
                    location = self.env["stock.location"].browse()
                parcels_quantity = sum(
                    package.number_of_parcels
                    for package in moves.move_line_ids.result_package_id
                )
                total_parcels += parcels_quantity
                if parcels_quantity:
                    total_location_parcels[location.id] = parcels_quantity
                product_quantity = sum(
                    move.quantity_done
                    for move in moves
                    if not move.move_line_ids.result_package_id
                )
                total_quantity += product_quantity
                if product_quantity:
                    total_quantities[location.id] = product_quantity
                locations.append(str(location.id))
            picking.parcels_and_items_per_source = {
                "parcels": total_location_parcels,
                "items": total_quantities,
                "parcels_total": total_parcels,
                "items_total": total_quantity,
                "locations": locations,
            }
