# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from odoo import api, fields, models
from odoo.fields import Command

from odoo.addons.shipment_advice.models.shipment_advice import ShipmentAdvice
from odoo.addons.stock.models.stock_location import Location

if TYPE_CHECKING:
    pass


class AlcReportShipmentAdvice(models.TransientModel):

    _name = "alc.report.shipment.advice"
    _description = "Shipment Advice Report for Alc"

    shipment_advice_id = fields.Many2one[ShipmentAdvice](
        ondelete="cascade",
        required=True,
    )
    parcels_and_items_per_source = fields.Json(
        compute="_compute_parcels_and_items_per_source",
    )
    line_ids = fields.One2many["AlcReportShipmentAdviceLine"](
        inverse_name="report_id",
    )
    location_ids = fields.Many2many[Location](
        compute="_compute_location_ids",
    )

    @api.depends("line_ids.parcels_and_items_per_source")
    def _compute_location_ids(self):
        # Gather all the locations from details as we need it to build
        # the locations table header.
        default_location = self.env["stock.location"].search(
            [("show_in_shipment_advice_report", "=", True)]
        )
        for report in self:
            line_ids = set()
            for line in report.line_ids:
                ids = line.parcels_and_items_per_source["locations"]
                line_ids.update(ids + default_location.ids)
            report.location_ids = [Command.set(line_ids)]

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
