# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from odoo.addons.alc_cerberus_utils import utils


class AlcEshopInfoMessage(models.Model):

    _inherit = "alc.eshop.info.banner"

    sync_state = fields.Selection(
        [
            ("new", "New"),
            ("to_update", "To update"),
            ("scheduled", "Scheduled"),
            ("done", "Done"),
        ],
        default="new",
        readonly=True,
    )

    # technical field. Never used. Used only to avoid but with methods searching
    # from index to bindings
    index_id = fields.Many2one("se.index", string="Index",)

    se_index_ids = fields.Many2many(
        comodel_name="se.index", compute="_compute_se_index"
    )

    json_doc = fields.Serialized(compute="_compute_json_doc")

    def write(self, vals):
        if "sync_state" not in vals:
            vals["sync_state"] = "to_update"
        return super(AlcEshopInfoMessage, self).write(vals)

    @api.model
    def _get_banners_to_sync(self):
        now = fields.Datetime.now()
        return self.search(
            [
                ("date_start", "<=", now),
                ("date_end", ">=", now),
                ("sync_state", "in", ["new", "to_update"]),
            ]
        )

    def _compute_se_index(self):
        model = self.env.ref("alc_eshop_info_banner.model_alc_eshop_info_banner")
        indexes = self.env["se.index"].search([("model_id", "=", model.id)])
        for rec in self:
            rec.se_index_ids = indexes

    def action_export_to_se(self):
        self.sudo().mapped(
            "se_index_ids.backend_id.specific_backend"
        ).export_info_banners(self)

    def _compute_json_doc(self):
        for rec in self:
            rec.json_doc = dict(
                id=rec.id,
                html=rec.html,
                date_start=utils.odoo_str_dt_to_dt_utc(rec.date_start).isoformat(),
                date_end=utils.odoo_str_dt_to_dt_utc(rec.date_end).isoformat(),
                type=rec.type,
            )
