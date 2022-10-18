# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AlcEshopAds(models.Model):

    _inherit = "alc.eshop.ads"

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
        return super(AlcEshopAds, self).write(vals)

    def unlink(self):
        for idx in self.sudo().mapped("se_index_ids"):
            idx.with_delay().delete_obsolete_item(self.ids)
        return super(AlcEshopAds, self).unlink()

    @api.model
    def _get_ads_to_sync(self):
        today = fields.Date.today()
        return self.search(
            [
                ("date_start", "<=", today),
                ("date_end", ">=", today),
                ("sync_state", "in", ["new", "to_update"]),
            ]
        )

    @api.model
    def _get_active_ads(self):
        today = fields.Date.today()
        return self.search([("date_start", "<=", today), ("date_end", ">=", today)])

    def _compute_se_index(self):
        model = self.env.ref("alc_eshop_ads.model_alc_eshop_ads")
        indexes = self.env["se.index"].search([("model_id", "=", model.id)])
        for rec in self:
            rec.se_index_ids = indexes

    def action_export_to_se(self):
        self.sudo().mapped("se_index_ids.backend_id.specific_backend").export_ads(self)

    def _compute_security(self):
        self.ensure_one()
        rights = ["is_alcyonnaire", "non_alcyonnaire"]
        if self.visibility == "non-shareholder":
            rights = ["non_alcyonnaire"]
        elif self.visibility == "shareholder":
            rights = ["is_alcyonnaire"]
        return rights

    def _compute_json_doc(self):
        for rec in self:
            doc = dict(
                id=rec.id,
                allowed_roles=",".join(rec._compute_security()),
                name=rec.name,
                date_start=rec.date_start,
                date_end=rec.date_end,
                site_url=rec.site_url or "",
                display_time=rec.display_time,
                display_slot=rec.display_slot,
                file=None,
                image=None,
            )
            if rec.file_id:
                doc.update(
                    {
                        "file": {
                            "url": rec.file_id.url,
                            "name": rec.file_id.name,
                            "mimetype": rec.file_id.mimetype or None,
                        }
                    }
                )
            if rec.image_id:
                doc.update(
                    {"image": {"name": rec.image_id.name, "url": rec.image_id.url}}
                )
            rec.json_doc = doc
