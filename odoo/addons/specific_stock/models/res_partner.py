# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    time_limit_order = fields.Float(
        'Deadline for ordering',
        compute='_compute_time_limit_order',
        readonly=True,
    )

    @api.multi
    def _compute_time_limit_order(self):
        """
        Compute the time limit of order

        We check for all round itinerary position
        with a default template version.
        The time limit of order must be round before the one quart of hour.
        :return:
        """
        query = """
        SELECT MIN(rt.time_picking_planned)
        FROM round_itinerary_position AS rip
          INNER JOIN round_itinerary ri ON rip.itinerary_id = ri.id
          INNER JOIN round_itinerary_round_template_rel rirtr
            ON ri.id = rirtr.round_itinerary_id
          INNER JOIN round_template AS rt ON rirtr.round_template_id = rt.id
          INNER JOIN round_template_round_template_version_rel rel
            ON rt.id = rel.round_template_id
          INNER JOIN round_template_version AS rtv
            ON rel.round_template_version_id = rtv.id
        WHERE rtv.is_default_version = TRUE
        AND rip.partner_id = %s;
        """

        for partner in self:
            self.env.cr.execute(query, (partner.id,))
            result = self.env.cr.fetchone()

            if not result or not result[0]:
                continue
            time_limit_order = result[0]

            hour = int(time_limit_order)
            minute = round(time_limit_order - hour, 2)

            if 0 < minute < 0.25:
                minute = 0
            elif 0.25 < minute < 0.50:
                minute = 0.25
            elif 0.50 < minute < 0.75:
                minute = 0.50
            elif minute > 0.75:
                minute = 0.75

            partner.time_limit_order = hour + minute
