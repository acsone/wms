# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import UserError


class Repair(models.Model):

    _inherit = "mrp.repair"

    @api.model
    def default_get(self, fields_list):
        defaults = super(Repair, self).default_get(fields_list)
        sav_location = self.env.ref(
            "alc_mrp_repair.sav_stock_location", raise_if_not_found=False
        )
        if sav_location:
            defaults["location_id"] = sav_location.id
            defaults["location_dest_id"] = sav_location.id
        return defaults

    def action_repair_cancel_draft(self):
        if self.filtered(lambda repair: repair.state == "under_repair"):
            raise UserError(
                _("Repair cannot be set to draft when it is already started.")
            )
        super(Repair, self).action_repair_cancel()
        return super(Repair, self).action_repair_cancel_draft()
