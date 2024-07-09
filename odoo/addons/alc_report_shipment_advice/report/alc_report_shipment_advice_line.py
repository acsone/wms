# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from collections import defaultdict

from odoo import api, fields, models

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.stock.models.stock_picking import Picking

from .alc_report_shipment_advice import AlcReportShipmentAdvice


class AlcReportShipmentAdviceLine(models.TransientModel):

    _name = "alc.report.shipment.advice.line"
    _description = "Shipment Advice Report Line for Alc"

    report_id = fields.Many2one[AlcReportShipmentAdvice](
        ondelete="cascade",
        required=True,
    )
    partner_id = fields.Many2one[Partner]()
    note = fields.Char()
    picking_ids = fields.Many2many[Picking]()
    parcels_and_items_per_source = fields.Json(
        compute="_compute_parcels_and_items_per_source",
    )

    parcels_and_items_per_category = fields.Json(
        compute="_compute_parcels_and_items_per_category",
    )

    @api.depends("picking_ids.parcels_and_items_per_source")
    def _compute_parcels_and_items_per_source(self):
        for line in self:
            total_location_parcels = defaultdict(int)
            total_quantities = defaultdict(int)  # Total of products without package
            total_parcels = 0
            total_quantity = 0.0
            locations = set()

            for picking in line.picking_ids:
                for location, value in picking.parcels_and_items_per_source[
                    "parcels"
                ].items():
                    location_id = int(location) if location.isnumeric() else False
                    total_location_parcels[location_id] += value
                    total_parcels += value
                    locations.update([location_id])
                for location, value in picking.parcels_and_items_per_source[
                    "items"
                ].items():
                    location_id = int(location) if location.isnumeric() else False
                    total_quantities[location_id] += value
                    total_quantity += value
                    locations.update([location_id])

            line.parcels_and_items_per_source = {
                "parcels": total_location_parcels,
                "items": total_quantities,
                "parcels_total": total_parcels,
                "items_total": total_quantity,
                "locations": list(locations),
            }

    @api.depends("picking_ids.package_level_ids_details")
    def _compute_parcels_and_items_per_category(self):
        for line in self:
            total_location_parcels = defaultdict(int)
            total_quantities = defaultdict(int)  # Total of products without package
            total_parcels = 0
            total_quantity = 0.0
            categories = set()

            for picking in line.picking_ids:
                for category_id, levels in picking.package_level_ids_details.filtered(
                    lambda level: not level.package_id.is_internal
                ).partition(lambda level: level.package_id.category_id):
                    value = sum(
                        [level.package_id.number_of_parcels for level in levels]
                    )
                    total_location_parcels[category_id] += sum(
                        [level.package_id.number_of_parcels for level in levels]
                    )
                    total_parcels += value
                    categories.update([category_id])
                for category_id, levels in picking.package_level_ids_details.filtered(
                    "package_id.is_internal"
                ).partition(lambda level: level.package_id.category_id):
                    value = sum(
                        [quant.quantity for quant in levels.package_id.quant_ids]
                    )
                    total_quantities[category_id] += value
                    total_quantity += value
                    categories.update([category_id])

            line.parcels_and_items_per_category = {
                "parcels": total_location_parcels,
                "items": total_quantities,
                "parcels_total": total_parcels,
                "items_total": total_quantity,
                "locations": list(categories),
            }
