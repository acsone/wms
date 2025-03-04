# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ShipmentAdvice(models.Model):

    _inherit = "shipment.advice"

    def create_toursolver_task(self):
        self.ensure_one()
        res = super().create_toursolver_task()
        self.toursolver_task_id.release_channel_id = self.release_channel_id
        return res
