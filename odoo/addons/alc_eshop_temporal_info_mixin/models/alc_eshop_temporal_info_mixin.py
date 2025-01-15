# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AlcEshopTemporalInfoMixin(models.AbstractModel):

    _name = "alc.eshop.temporal.info.mixin"
    _description = "Alc Eshop Temporal Info"

    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True)
    is_published = fields.Boolean(string="Published?", readonly=True)

    def action_toggle_is_published(self):
        for record in self:
            record.is_published = not record.is_published

    @api.constrains("date_start", "date_end")
    def _validate_dates(self):
        for this in self:
            start = fields.Datetime.to_datetime(this.date_start)
            end = fields.Datetime.to_datetime(this.date_end)
            if start > end:
                raise ValidationError(
                    _(
                        "The defined period is not valid (%(start)s > %(end)s)",
                        start=this.date_start,
                        end=this.date_end,
                    )
                )
