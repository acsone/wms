# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from itertools import groupby

from odoo import api, fields, models


class MakeTodayDeliveryPlan(models.TransientModel):
    _name = "round.wizard.makeplan"

    version_id = fields.Many2one(
        "round.template.version",
        string="Version",
        required=True,
        default=lambda x: x.env["round.template.version"].search(
            [("is_default_version", "=", True)]
        ),
    )
    assign_moves = fields.Boolean("Reserve stock", default=True)
    tag_ids = fields.Many2many(
        "round.tag",
        string="Tags",
        help="Only templates having one of the tags will be instanciated",
    )
    execution_date = fields.Date(
        "Date", default=fields.Date.context_today, required=True
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        round_instance = self.env["round.instance"]
        templates = self.version_id.template_ids.filtered(
            lambda t: any(tag in t.tag_ids for tag in self.tag_ids)
        )
        execution_date = self.execution_date
        instances = round_instance.search(
            [("date", "=", execution_date)], order="template_id"
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
                round_instance.create(
                    {
                        "template_id": template.id,
                        "state": "draft",
                        "itinerary_ids": [(6, 0, template.itinerary_ids.ids)],
                        "date": execution_date,
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
