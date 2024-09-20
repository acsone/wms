# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from odoo import api, fields, models
from odoo.fields import Command

from odoo.addons.shipment_advice.models.shipment_advice import ShipmentAdvice
from odoo.addons.stock.models.stock_location import Location
from odoo.addons.stock_package_type_category.models.stock_package_type_category import (
    StockPackageTypeCategory,
)

if TYPE_CHECKING:
    pass


class AlcReportShipmentAdvice(models.TransientModel):

    _name = "alc.report.shipment.advice"
    _description = "Shipment Advice Report for Alc"

    shipment_advice_id = fields.Many2one[ShipmentAdvice](
        ondelete="cascade",
        required=True,
    )
    # TODO: Remove this
    parcels_and_items_per_source = fields.Json(
        compute="_compute_parcels_and_items_per_source",
    )
    parcels_and_items_per_category = fields.Json(
        compute="_compute_parcels_and_items_per_category",
    )
    line_ids = fields.One2many["AlcReportShipmentAdviceLine"](
        inverse_name="report_id",
    )
    location_ids = fields.Many2many[Location](
        compute="_compute_location_ids",
    )
    category_ids = fields.Many2many[StockPackageTypeCategory](
        compute="_compute_category_ids",
    )

    @api.depends("line_ids.parcels_and_items_per_source")
    def _compute_location_ids(self):
        # Gather all the locations from details as we need it to build
        # the locations table header.
        location_obj = self.env["stock.location"]
        default_locations = location_obj.search(
            [("show_in_shipment_advice_report", "=", True)]
        )
        for report in self:
            line_ids = set()
            for line in report.line_ids:
                ids = line.parcels_and_items_per_source["locations"]
                line_ids.update(ids + default_locations.ids)
            sorted_location_ids = (
                location_obj.browse(line_ids)
                .sorted("sequence_in_shipment_advice_report")
                .ids
            )
            if False in line_ids:
                sorted_location_ids = [False] + sorted_location_ids
            report.location_ids = [Command.set(sorted_location_ids)]

    @api.depends("line_ids.picking_ids.parcels_and_items_per_source")
    def _compute_parcels_and_items_per_source(self):
        # Sum all lines values in order to compute totals in advance
        for advice in self:
            total_parcels = 0
            total_items = 0
            total = 0
            total_zone_parcels = defaultdict(lambda: 0)
            total_zone_items = defaultdict(lambda: 0)
            total_zone = defaultdict(lambda: 0)
            for line in self.line_ids:
                paips = line.parcels_and_items_per_source
                for zone in paips["locations"]:
                    sz_zone = str(zone).lower()  # because it can be False
                    total_parcels += paips["parcels"].get(sz_zone, 0)
                    total_items += paips["items"].get(sz_zone, 0)
                    total_zone_parcels[sz_zone] += paips["parcels"].get(sz_zone, 0)
                    total_zone[sz_zone] += paips["parcels"].get(sz_zone, 0)
                    total_zone_items[sz_zone] += paips["items"].get(sz_zone, 0)
                    total_zone[sz_zone] += paips["items"].get(sz_zone, 0)
                total += total_parcels + total_items
            advice.parcels_and_items_per_source = {
                "total_parcels": total_parcels,
                "total_items": total_items,
                "total": total,
                "total_zone_parcels": dict(total_zone_parcels),
                "total_zone_items": dict(total_zone_items),
                "total_zone": dict(total_zone),
            }

    @api.depends("line_ids")
    def _compute_category_ids(self):
        """This will compute the categories to display as headers."""
        category_obj = self.env["stock.package.type.category"]
        categories = category_obj.search([]).sorted(
            "sequence_in_shipment_advice_report"
        )
        for report in self:
            report.category_ids = categories

    @api.depends_context("company")
    @api.depends("line_ids.parcels_and_items_per_category")
    def _compute_parcels_and_items_per_category(self):
        for report in self:
            total_parcels = 0
            total_items = 0
            total = 0
            total_category_parcels = defaultdict(lambda: 0)
            total_category_items = defaultdict(lambda: 0)
            total_category = defaultdict(lambda: 0)
            for line in report.line_ids:
                category_lines = line.parcels_and_items_per_category
                for category in category_lines.get("categories"):
                    one_category = str(category).lower()
                    total_parcels += category_lines["parcels"].get(one_category, 0)
                    total_items += category_lines["items"].get(one_category, 0)
                    total_category_parcels[one_category] += category_lines[
                        "parcels"
                    ].get(one_category, 0)
                    total_category[one_category] += category_lines["parcels"].get(
                        one_category, 0
                    )
                    total_category_items[one_category] += category_lines["items"].get(
                        one_category, 0
                    )
                    total_category[one_category] += category_lines["items"].get(
                        one_category, 0
                    )

            report.parcels_and_items_per_category = {
                "total_parcels": total_parcels,
                "total_items": total_items,
                "total": total,
                "total_category_parcels": dict(total_category_parcels),
                "total_category_items": dict(total_category_items),
                "total_category": dict(total_category),
            }
