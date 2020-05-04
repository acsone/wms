# -*- coding: utf-8 -*-
# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = "account.analytic.account"

    tag_1_id = fields.Many2one(
        "account.analytic.tag",
        string="Tag 1",
        compute="_compute_tag_id",
        store=True,
        index=True,
    )
    tag_2_id = fields.Many2one(
        "account.analytic.tag",
        string="Tag 2",
        compute="_compute_tag_id",
        store=True,
        index=True,
    )
    tag_3_id = fields.Many2one(
        "account.analytic.tag",
        string="Tag 3",
        compute="_compute_tag_id",
        store=True,
        index=True,
    )

    @api.depends("tag_ids")
    def _compute_tag_id(self):
        for rec in self:
            tags_by_color = {t.color: t for t in rec.tag_ids}
            rec.tag_1_id = tags_by_color.get(1, False)
            rec.tag_2_id = tags_by_color.get(2, False)
            rec.tag_3_id = tags_by_color.get(3, False)
