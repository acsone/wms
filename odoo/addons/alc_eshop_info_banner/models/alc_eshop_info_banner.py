# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AlcEshopInfoBanner(models.Model):

    _name = "alc.eshop.info.banner"
    _description = "Eshop Info Banner"

    html = fields.Html(required=True, translate=True)
    type = fields.Selection(
        selection=[("info", "info"), ("warning", "warning")],
        required=True,
        default="info",
    )
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    @api.constrains("date_start", "date_end")
    def _validate_dates(self):
        for this in self:
            start = fields.Date.from_string(this.date_start)
            end = fields.Date.from_string(this.date_end)
            if start > end:
                raise ValidationError(
                    _("The defined period is not a valid (%s > %s)")
                    % (this.date_start, this.date_end)
                )
