# © 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shipment_advice.models.shipment_advice import ShipmentAdvice as Advice


class ShipmentAdvice(Advice):
    def print_all_deliveryslip(self):
        ship_type = self.env.ref("stock.picking_type_out")
        shippings = (
            (self.loaded_picking_ids | self.rma_picking_ids)
            .sorted("toursolver_shipment_advice_rank")
            .filtered(
                lambda ship: ship.picking_type_id == ship_type
                or ship.picking_type_id.is_rma
            )
        )
        return self.env.ref("stock.action_report_delivery").report_action(shippings)
