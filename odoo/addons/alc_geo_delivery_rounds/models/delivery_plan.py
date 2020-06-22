# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class DeliveryPlan(models.Model):
    _name = "delivery.plan"
    _description = "Delivery plan"

    name = fields.Char(required=True)
    _sql_constraints = [("name_uniq", "UNIQUE(name)", _("Name must be unique"))]

    round_template_ids = fields.One2many(
        comodel_name="round.template",
        inverse_name="delivery_plan_id",
        string="Templates",
    )

    @api.multi
    def action_shape_file_import(self):
        return self.env.ref("alc_geo_delivery_rounds.action_shape_file_import").read()[
            0
        ]
