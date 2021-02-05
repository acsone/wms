# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RoundTemplate(models.Model):

    _inherit = "round.template"

    geo_optimization_enabled = fields.Boolean("Enable geo optimization")

    geo_optimization_resource_id = fields.Selection(
        selection="_selection_geo_optimization_resource_id"
    )
    geo_optimization_method = fields.Selection(
        selection="_selection_geo_optimization_method"
    )

    @api.model
    def _selection_geo_optimization_resource_id(self):
        resource_number = self.get_optimization_config().resources_number
        return [("D%d" % (i + 1), "D%d" % (i + 1)) for i in range(resource_number)]

    @api.model
    def _selection_geo_optimization_method(self):
        return (
            self.env["stock.config.settings"]
            ._fields["geo_optimization_method"]
            .selection
        )

    @api.constrains("geo_optimization_enabled", "geo_optimization_resource_id")
    def _check_geo_optimization_resource_id(self):
        for rec in self:
            if rec.geo_optimization_enabled and not rec.geo_optimization_resource_id:
                raise ValidationError(
                    _(
                        "A resource identifier is required if geo_optimization is enabled for %s"
                    )
                    % rec.display_name
                )

    @api.model
    def get_optimization_config(self):
        return self.env["stock.config.settings"].get_optimization_config()
