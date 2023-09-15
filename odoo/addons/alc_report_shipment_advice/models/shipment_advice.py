# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields
from odoo.fields import Command

from odoo.addons.shipment_advice_planner_toursolver.models.shipment_advice import (
    ShipmentAdvice as Advice,
)


class ShipmentAdvice(Advice):

    parcels_and_items_per_source = fields.Json(
        compute="_compute_parcels_and_items_per_source",
    )

    def _compute_parcels_and_items_per_source(self):
        for advice in self:
            pickings = self._get_sorted_shipping_ids()
            total_parcels = 0
            total_items = 0
            total = 0
            for picking in pickings:
                total_parcels += sum(
                    list(picking.parcels_and_items_per_source["parcels"].values())
                )
                total_items += sum(
                    list(picking.parcels_and_items_per_source["items"].values())
                )
            total = total_parcels + total_items
            advice.parcels_and_items_per_source = {
                "total_parcels": total_parcels,
                "total_items": total_items,
                "total": total,
            }

    def _get_sorted_shipping_ids(self):
        """Return the shippings into the expected delivery order."""
        self.ensure_one()
        return self.loaded_picking_ids.sorted("toursolver_shipment_advice_rank")

    def _get_location_zones(self, pickings):
        # This will gather all source (Stock) locations zones from parcels numbers and isolated
        # products
        self.ensure_one()
        keys = []
        for picking in pickings:
            if picking.parcels_and_items_per_source:
                keys.extend(
                    [
                        int(key)
                        for key in picking.parcels_and_items_per_source["locations"]
                    ]
                )
        return self.env["stock.location"].browse(keys)

    def _get_alc_report_line_values(self, pickings):
        self.ensure_one()
        if self.toursolver_resource_id:
            pickings = pickings.filtered(
                lambda p, resource=self.toursolver_resource_id: p.toursolver_resource_id
                == resource
            )
        # We want to group shippings for a same partner
        self.env["alc.report.shipment.advice.line"].browse()
        line_values = []
        for partner, partner_shippings in pickings.partition("partner_id").items():
            line_values.append(
                {
                    "partner_id": partner.id,
                    "note": partner.comment,
                    "picking_ids": [Command.set(partner_shippings.ids)],
                }
            )
        return line_values

    def get_alc_report_shipment_advice(self):
        # Entry point to get the report
        self.ensure_one()
        shippings = self._get_sorted_shipping_ids()
        report = self.env["alc.report.shipment.advice"].create(
            {
                "shipment_advice_id": self.id,
                "line_ids": [
                    Command.create(value)
                    for value in self._get_alc_report_line_values(shippings)
                ],
            }
        )

        return report
