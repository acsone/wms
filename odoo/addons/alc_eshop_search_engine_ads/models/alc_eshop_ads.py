# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.models import Model

from odoo.addons.connector_search_engine.models.se_index import SeIndex


class AlcEshopAds(Model):

    _name = "alc.eshop.ads"
    _inherit = ["alc.eshop.ads", "se.indexable.record"]
    se_index_ids = fields.Many2many[SeIndex](compute="_compute_se_index")

    @api.depends("lang_id")
    def _compute_se_index(self):
        model = self.env.ref("alc_eshop_ads.model_alc_eshop_ads")
        all_indexes = self.env["se.index"].search([("model_id", "=", model.id)])
        for rec in self:
            indexes = all_indexes
            if rec.lang_id:
                indexes = all_indexes.filtered(
                    lambda i, record=rec: i.lang_id == record.lang_id
                )
            rec.se_index_ids = indexes

    def action_toggle_is_published(self):
        res = super().action_toggle_is_published()
        self._compute_se_index()
        for rec in self:
            if rec.is_published:
                rec._add_to_index(rec.se_index_ids)
            else:
                rec._remove_from_index(rec.se_index_ids)
        return res

    def action_synchronize_ads(self):
        for rec in self:
            rec.button_synchronize_ads()

    def _ensure_ads_in_right_indexes(self):
        for record in self:
            if not record.is_published:
                if record.se_binding_ids:
                    record._remove_from_index(record.se_binding_ids.index_id)
                continue
            if record.lang_id:
                wrong_bindings = record.se_binding_ids.filtered(
                    lambda i, record=record: i.index_id.lang_id != record.lang_id
                )
                if wrong_bindings:
                    record._remove_from_index(wrong_bindings.index_id)
                if not record.se_binding_ids.filtered(
                    lambda i, record=record: i.index_id.lang_id == record.lang_id
                ):
                    if record.se_index_ids:
                        record._add_to_index(record.se_index_ids)

    def button_synchronize_ads(self):
        self.ensure_one()
        # remove binding that are in an specific language and present in the
        # wrong indexes
        self._ensure_ads_in_right_indexes()
        self.filtered_domain(self._get_ads_to_export_domain()).se_binding_ids.filtered(
            lambda i: i.state != "to_delete"
        ).recompute_json()
        self.filtered_domain(
            self._get_ads_to_delete_domain()
        ).action_toggle_is_published()

    @api.model
    def _get_ads_to_export_domain(self):
        now = fields.Datetime.now()
        return [
            ("date_end", ">=", now),
            ("is_published", "=", True),
        ]

    @api.model
    def _get_ads_to_delete_domain(self):
        now = fields.Datetime.now()
        return [
            ("is_published", "=", True),
            ("date_end", "<", now),
        ]

    def write(self, vals):
        self._se_mark_to_update()
        return super().write(vals)

    def _compute_security(self):
        self.ensure_one()
        rights = ["is_alcyonnaire", "is_alcyonnaire_under_contract", "non_alcyonnaire"]
        if self.visibility == "non-shareholder":
            rights = ["non_alcyonnaire"]
        elif self.visibility == "shareholder":
            rights = ["is_alcyonnaire"]
        elif self.visibility == "shareholder-under-contract":
            rights = ["is_alcyonnaire_under_contract"]
        return rights
