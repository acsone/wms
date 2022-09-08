# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RoundTemplate(models.Model):

    _inherit = "round.template"

    geo_optimization_enabled = fields.Boolean("Enable geo optimization")

    geo_optimization_method = fields.Selection(
        selection="_selection_geo_optimization_method"
    )

    delivery_resource_ids = fields.Many2many(comodel_name="alc.delivery.resource")

    @api.model
    def _selection_geo_optimization_method(self):
        return (
            self.env["stock.config.settings"]
            ._fields["geo_optimization_method"]
            .selection
        )

    @api.constrains("geo_optimization_enabled", "delivery_resource_ids")
    def _check_delivery_resource_ids(self):
        for rec in self:
            if rec.geo_optimization_enabled and not rec.delivery_resource_ids:
                raise ValidationError(
                    _(
                        "A delivery resource is required if geo_optimization is enabled for %s"
                    )
                    % rec.display_name
                )
