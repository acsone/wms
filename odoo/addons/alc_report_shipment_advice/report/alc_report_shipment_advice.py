# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from __future__ import annotations

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
        for report in self:
            line_ids = set()
            for line in report.line_ids:
                ids = line.parcels_and_items_per_source["locations"]
                line_ids.update(ids)
            report.location_ids = [Command.set(line_ids)]

    @api.depends("line_ids.picking_ids.parcels_and_items_per_source")
    def _compute_parcels_and_items_per_source(self):
        # Sum all lines values in order to compute totals in advance
        for advice in self:
            total_parcels = 0
            total_items = 0
            total = 0
            for picking in self.line_ids.picking_ids:
                total_parcels += sum(
                    list(picking.parcels_and_items_per_source["parcels"].values())
                )
                total_items += sum(
                    list(picking.parcels_and_items_per_source["items"].values())
                )
                total += total_parcels + total_items
            advice.parcels_and_items_per_source = {
                "total_parcels": total_parcels,
                "total_items": total_items,
                "total": total,
            }
