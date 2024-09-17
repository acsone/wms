# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.shipment_advice.models.shipment_advice import (
    ShipmentAdvice as ShipmentAdviceBase,
)
from odoo.addons.stock.models.stock_picking import Picking


class ShipmentAdvice(ShipmentAdviceBase):
    rma_picking_ids = fields.One2many[Picking](
        inverse_name="rma_shipment_advice_id",
        string="RMA Pickings",
        help="List of RMA pickings linked to this shipment advice.",
    )

    rma_pickings_count = fields.Integer(
        string="RMA Pickings Count",
        compute="_compute_rma_pickings_count",
        help="Number of RMA pickings linked to this shipment advice.",
    )

    @api.depends("rma_picking_ids")
    def _compute_rma_pickings_count(self):
        for rec in self:
            rec.rma_pickings_count = len(rec.rma_picking_ids)

    def _postprocess_action_done(self):
        self.ensure_one()
        res = super()._postprocess_action_done()
        if self.state == "done":
            self._link_rma_picking()
        return res

    def _link_rma_picking_domain(self):
        self.ensure_one()
        return [
            ("picking_type_id.is_rma", "=", True),
            ("rma_shipment_advice_id", "=", False),
            ("partner_id", "in", self.loaded_picking_ids.partner_id.ids),
            ("state", "=", "assigned"),
        ]

    def _link_rma_picking(self):
        pickings = self.env["stock.picking"].search(self._link_rma_picking_domain())
        pickings.rma_shipment_advice_id = self

    def button_open_rma_pickings(self):
        action_xmlid = "stock.action_picking_tree_all"
        action = self.env["ir.actions.act_window"]._for_xml_id(action_xmlid)
        action["domain"] = [("id", "in", self.rma_picking_ids.ids)]
        return action
