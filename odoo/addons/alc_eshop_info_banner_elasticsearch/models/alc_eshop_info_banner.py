# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields
from odoo.models import Model

from odoo.addons.connector_search_engine.models.se_index import SeIndex


class AlcEshopInfoMessage(Model):
    _name = "alc.eshop.info.banner"
    _inherit = ["alc.eshop.info.banner", "se.indexable.record"]
    se_index_ids = fields.Many2many[SeIndex](compute="_compute_se_index")

    def _compute_se_index(self):
        model = self.env.ref("alc_eshop_info_banner.model_alc_eshop_info_banner")
        indexes = self.env["se.index"].search([("model_id", "=", model.id)])
        self.update({"se_index_ids": [Command.set(indexes.ids)]})

    def action_toggle_is_published(self):
        res = super().action_toggle_is_published()
        self._compute_se_index()
        for rec in self:
            if rec.is_published:
                rec._add_to_index(rec.se_index_ids)
            else:
                rec._remove_from_index(rec.se_index_ids)
        return res

    def action_synchronize_info_banners(self):
        for rec in self:
            rec.button_synchronize_info_banner()

    def button_synchronize_info_banner(self):
        self.ensure_one()
        self.filtered_domain(
            self._get_banner_to_export_domain()
        ).se_binding_ids.recompute_json()
        self.filtered_domain(
            self._get_banner_to_delete_domain()
        ).action_toggle_is_published()

    @api.model
    def _get_banner_to_export_domain(self):
        now = fields.Datetime.now()
        return [
            ("date_start", "<=", now),
            ("date_end", ">=", now),
            ("is_published", "=", True),
        ]

    @api.model
    def _get_banner_to_delete_domain(self):
        now = fields.Datetime.now()
        return [
            ("is_published", "=", True),
            "|",
            ("date_start", ">", now),
            ("date_end", "<", now),
        ]

    def write(self, vals):
        self._se_mark_to_update()
        return super().write(vals)
