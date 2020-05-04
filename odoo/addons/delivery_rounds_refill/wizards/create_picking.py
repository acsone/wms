# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models


class ReportStockRefillWizard(models.TransientModel):
    _name = "report.stock.refill.wizard"

    @api.multi
    def confirm(self):
        model = self._context["active_model"]
        assert model in (
            "report.stock.refill.arrange",
            "report.stock.refill.reassort",
        ), "Invalid Model"

        pickings = self.env["stock.picking"]
        for report in self.env[model].browse(self._context["active_ids"]):
            picking = report.create_picking()
            pickings |= picking

        if model == "report.stock.refill.arrange":
            name = _("Parking")
        else:
            name = _("Reserve")

        action = {
            "name": name,
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "view_type": "form",
        }

        if len(pickings) == 1:
            action.update({"view_mode": "form", "res_id": picking.id})
        else:
            action.update(
                {"view_mode": "tree,form", "domain": [("id", "in", pickings.ids)]}
            )

        return action
