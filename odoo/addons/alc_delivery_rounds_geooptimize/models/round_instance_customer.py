# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RoundInstanceCustomer(models.Model):

    _inherit = "round.instance.customer"

    is_rank_computed = fields.Boolean(readonly=True)

    delivery_resource_id = fields.Many2one(
        comodel_name="alc.delivery.resource", string="Image", ondelete="set null",
    )

    def _fields_to_propagate_to_picks(self):
        flds = super(RoundInstanceCustomer, self)._fields_to_propagate_to_picks()
        flds.append("delivery_resource_id")
        return flds

    def _prepare_data_to_propagate(self):
        data = super(RoundInstanceCustomer, self)._prepare_data_to_propagate()
        data["delivery_resource_id"] = self.delivery_resource_id.id
        return data
