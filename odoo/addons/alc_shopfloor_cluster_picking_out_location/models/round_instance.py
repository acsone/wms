# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class RoundInstance(models.Model):

    _inherit = "round.instance"

    def _deliver(self, background=True):
        res = super(RoundInstance, self)._deliver(background=background)

        out_location = self.env.ref("stock.stock_location_output")
        out_locations_to_clean = self.env["stock.location"].search(
            [("id", "child_of", out_location.id), ("delivery_round_id", "in", self.ids)]
        )

        out_locations_to_clean.write({"delivery_round_id": None})
        return res
