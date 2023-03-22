# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import typing

from odoo import _, fields, models

if typing.TYPE_CHECKING:
    pass


class AlcDeliveryPlan(models.Model):

    _name = "alc.delivery.plan"
    _description = "Alc Delivery Plan"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    release_channel_ids = fields.One2many["StockReleaseChannel"](
        inverse_name="delivery_plan_id",
        string="Channels",
        readonly=True,
    )

    _sql_constraints = [("name_uniq", "UNIQUE(name)", _("Name must be unique"))]

    def action_import_release_channels(self):
        return self.env.ref(
            "alc_stock_release_channel_import.alc_import_delivery_zone_wizard_act_window"
        ).read()[0]

    def action_show_channels(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "stock.release.channel",
            "domain": [("delivery_plan_id", "=", self.id)],
            "context": {"create": False},
            "name": _("Release Channels"),
            "view_mode": "geoengine,kanban,tree,form",
        }

    def write(self, vals):
        res = super().write(vals)
        inactive = self.filtered(lambda r: not r.active)
        inactive.release_channel_ids.write({"active": False})
        return res
