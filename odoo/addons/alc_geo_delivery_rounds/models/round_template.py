# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields
from odoo.addons.base_geoengine import fields as geo_fields, geo_model
from odoo.exceptions import ValidationError


class RoundTemplate(geo_model.GeoModel):
    _inherit = "round.template"

    delivery_plan_id = fields.Many2one("delivery.plan", string="Delivery")
    geo_polygon_shape = geo_fields.GeoMultiPolygon("Delivery round Shape")

    @api.constrains("delivery_plan_id", "geo_polygon_shape")
    def _check_geo_polygon_shape(self):
        for rec in self:
            if rec.delivery_plan_id and not rec.geo_polygon_shape:
                raise ValidationError(
                    _("A shape is required if a delivery plan is set for %s")
                    % rec.display_name
                )

    @api.multi
    @api.depends("name", "code", "tag_ids", "delivery_plan_id")
    def name_get(self):
        templates_with_delivery = []
        templates_without_delivery = []

        for rec in self:
            if rec.delivery_plan_id:
                templates_with_delivery.append(rec.id)
            else:
                templates_without_delivery.append(rec.id)

        result = super(
            RoundTemplate, self.browse(templates_without_delivery)
        ).name_get()

        for rec in self.browse(templates_with_delivery):
            result.append((rec.id, "{}-{}".format(rec.delivery_plan_id.name, rec.name)))

        return result
