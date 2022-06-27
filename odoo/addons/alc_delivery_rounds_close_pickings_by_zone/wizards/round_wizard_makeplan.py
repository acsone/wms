# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class RoundWizardMakeplan(models.TransientModel):

    _inherit = "round.wizard.makeplan"

    def _initialize_delivery_rounds(self):
        delivery_round_ids = super(
            RoundWizardMakeplan, self
        )._initialize_delivery_rounds()
        delivery_rounds = self.env["round.instance"].browse(delivery_round_ids)
        for delivery_round in delivery_rounds:
            if (
                delivery_round.auto_close_picking_launched
                and delivery_round.time_reopen_picking_launched
            ):
                delivery_round._delay_reopen_pickings()
        return delivery_round_ids
