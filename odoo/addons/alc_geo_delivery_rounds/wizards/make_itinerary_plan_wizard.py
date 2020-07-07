# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from itertools import groupby

from odoo import api, fields, models


class MakeItineraryPlanWizard(models.TransientModel):

    _name = "make.itinerary.plan.wizard"

    delivery_plan_id = fields.Many2one(
        "delivery.plan",
        string="Delivery plan",
        required=True,
        default=lambda x: x._default_delivery_plan_id(),
    )
    execution_date = fields.Date(
        "Date", default=fields.Date.context_today, required=True
    )

    assign_moves = fields.Boolean("Reserve stock", default=True)
    tag_ids = fields.Many2many("round.tag", string="Tags")

    @api.model
    def _default_delivery_plan_id(self):
        return self.env["delivery.plan"].browse(self.env.context.get("active_ids")).id

    @api.multi
    def confirm(self):
        self.ensure_one()
        templates = self.delivery_plan_id.round_template_ids
        instances = self.env["round.instance"].search(
            [("date", "=", self.execution_date)], order="template_id"
        )

        instances_by_template = dict(groupby(instances, key=lambda r: r.template_id))
        for template in templates:
            if template in instances_by_template:
                for instance in instances_by_template.pop(template):
                    if instance.state == "pending":
                        instance.state = "draft"
                    if (
                        not instance.time_picking_planned
                        or not instance.time_leave_planned
                    ):
                        instance.write(
                            {
                                "time_picking_planned": template.time_picking_planned,
                                "time_leave_planned": template.time_leave_planned,
                            }
                        )
            else:
                self.env["round.instance"].create(
                    {
                        "template_id": template.id,
                        "state": "draft",
                        "itinerary_ids": [(6, 0, template.itinerary_ids.ids)],
                        "date": self.execution_date,
                        "time_picking_planned": template.time_picking_planned,
                        "time_leave_planned": template.time_leave_planned,
                        "tag_ids": [(6, 0, self.tag_ids.ids)],
                    }
                )

        if templates and self.assign_moves:
            # Run stock reservations in background.  This process automatically
            # assign pickings and shippings to available delivery rounds
            StockPicking = self.env["stock.picking"]
            StockPicking._delay_jobs_action_assign()

        return self.env["ir.actions.act_window"].for_xml_id(
            "delivery_rounds", "action_round_instance"
        )
