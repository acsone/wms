# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.connector_search_engine.models.se_index import SeIndex


class AlcEshopTemporalInfoMixin(models.AbstractModel):

    _name = "alc.eshop.temporal.info.mixin"
    _inherit = [
        "alc.eshop.temporal.info.mixin",
        "se.indexable.record",
    ]  # nosemgrep: is-old-style-inheritance
    _description = "Alc Eshop Temporal Info"

    se_index_ids = fields.Many2many[SeIndex](compute="_compute_se_index")

    def _compute_se_index(self):
        pass

    def action_toggle_is_published(self):
        res = super().action_toggle_is_published()
        self._compute_se_index()
        for rec in self:
            if rec.is_published:
                rec._add_to_index(rec.se_index_ids)
            else:
                rec._remove_from_index(rec.se_index_ids)
        return res

    def action_synchronize_records(self):
        for rec in self:
            rec.button_synchronize_records()

    def button_synchronize_records(self):
        self.ensure_one()
        self.filtered_domain(
            self._get_records_to_export_domain()
        ).se_binding_ids.filtered(lambda i: i.state != "to_delete").recompute_json()
        self.filtered_domain(
            self._get_records_to_delete_domain()
        ).action_toggle_is_published()

    @api.model
    def _get_records_to_export_domain(self):
        now = fields.Datetime.now()
        return [
            ("date_end", ">=", now),
            ("is_published", "=", True),
        ]

    @api.model
    def _get_records_to_delete_domain(self):
        now = fields.Datetime.now()
        return [
            ("is_published", "=", True),
            ("date_end", "<", now),
        ]

    def write(self, vals):
        self._se_mark_to_update()
        return super().write(vals)
