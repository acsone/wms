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
                    total_location_parcels[int(location)] += value
                    total_parcels += value
                    locations.update([int(location)])
                for location, value in picking.parcels_and_items_per_source[
                    "items"
                ].items():
                    total_quantities[int(location)] += value
                    total_quantity += value
                    locations.update([int(location)])

            line.parcels_and_items_per_source = {
                "parcels": total_location_parcels,
                "items": total_quantities,
                "parcels_total": total_parcels,
                "items_total": total_quantity,
                "locations": list(locations),
            }
