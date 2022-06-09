# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    alc_classified_ids = fields.One2many(
        "alc.classified", "partner_id", string="Classifieds"
    )

    alc_classified_count = fields.Integer(
        compute="_compute_alc_classified_count", string="# of classifieds",
    )

    @api.depends("alc_classified_ids")
    def _compute_alc_classified_count(self):
        results = self.env["alc.classified"].read_group(
            [("partner_id", "in", self.ids)], fields=0, groupby=["partner_id"]
        )
        counts = {r["partner_id"][0]: r["partner_id_count"] for r in results}
        for partner in self:
            partner.alc_classified_count = counts.get(partner.id, 0)

    def action_show_classifieds(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Classifieds"),
            "res_model": "alc.classified",
            "domain": [("partner_id", "=", self.id)],
            "view_type": "form",
            "view_mode": "tree, form",
            "context": self.env.context,
            "target": "current",
        }
