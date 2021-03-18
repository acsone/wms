# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):

    _inherit = "res.partner"

    use_specific_delivery_duration = fields.Boolean(
        "Change the default delivery duration",
        help="Change the default delivery duration for this specific partner",
        default=False,
    )
    delivery_duration = fields.Integer(compute="_compute_delivery_duration")
    specific_delivery_duration = fields.Integer(
        "Delivery duration",
        required=False,
        help="Duration in seconds needed to deliver a specific customer (different from the general one)",
    )

    @api.constrains("specific_delivery_duration", "use_specific_delivery_duration")
    def _check_specific_delivery_duration(self):
        for rec in self:
            if (
                rec.use_specific_delivery_duration
                and not rec.specific_delivery_duration
            ):
                raise ValidationError(
                    _(
                        "If you enable the specific delivery duration for this user, you must provide a duration."
                    )
                )

    @api.multi
    def write(self, vals):
        if (
            "use_specific_delivery_duration" in vals
            and not vals["use_specific_delivery_duration"]
        ):
            vals["specific_delivery_duration"] = False
            self.invalidate_cache(["delivery_duration"], self.ids)
        return super(ResPartner, self).write(vals)

    def _compute_delivery_duration(self):
        cfg = self.env["stock.config.settings"].get_optimization_config()
        for rec in self:
            rec.delivery_duration = (
                rec.specific_delivery_duration or cfg.delivery_duration
            )
