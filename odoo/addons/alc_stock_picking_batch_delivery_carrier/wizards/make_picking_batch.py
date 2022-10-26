# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class MakePickingBatch(models.TransientModel):

    _inherit = "make.picking.batch"

    delivery_carrier_ids = fields.Many2many(
        comodel_name="delivery.carrier",
        string="Delivery Methods allowed for the cluster",
        help="List of eligible device methods when creating a batch transfer",
    )

    def _get_delivery_rounds(self, picking_type_ids, operator):
        delivery_rounds_authorized = self.env["round.instance"]
        delivery_rounds = super(MakePickingBatch, self)._get_delivery_rounds(
            picking_type_ids, operator
        )
        delivery_rounds_by_carrier = delivery_rounds.partition(
            "shipping_ids.carrier_id"
        )
        for carrier, grouped_delivery_rounds in delivery_rounds_by_carrier.items():
            if carrier in self.delivery_carrier_ids:
                delivery_rounds_authorized |= grouped_delivery_rounds

        if not delivery_rounds_authorized:
            msg = (
                "No delivery round to prepare for the delivery method(s) you choose: %s"
                % self.delivery_carrier_ids.mapped("name")
            )
            raise ValidationError(_(msg))
        return delivery_rounds_authorized
