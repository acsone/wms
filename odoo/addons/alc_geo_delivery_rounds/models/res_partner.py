# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    tag_ids = fields.Many2many(
        "round.tag",
        string="Tags",
        help="Only partners with the right tag will be delivered",
    )

    round_template_ids = fields.Many2many(
        "round.template",
        string="Round templates",
        help="List all the round templates containing the partner",
        compute="_compute_round_template_ids",
    )

    tag_labels = fields.Char(compute="_compute_tag_labels")

    @api.multi
    @api.depends("geo_point", "round_template_ids.geo_polygon_shape")
    def _compute_round_template_ids(self):
        self.env.cr.execute(
            """
            SELECT res_partner.id, round_template.id
            FROM res_partner JOIN round_template ON
            ST_contains(round_template.geo_polygon_shape, res_partner.geo_point)
            """
        )

        templates_by_partner = defaultdict(list)
        for partner_id, round_template_id in self.env.cr.fetchall():
            templates_by_partner[partner_id].append(round_template_id)

        for record in self:
            templates_ids = templates_by_partner.get(record.id, [])
            record.round_template_ids = self.env["round.template"].browse(templates_ids)

    @api.depends("tag_ids")
    def _compute_tag_labels(self):
        for record in self:
            record.tag_labels = ",  ".join(record.mapped("tag_ids.name"))
