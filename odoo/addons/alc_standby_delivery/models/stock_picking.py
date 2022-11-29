# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    checksum = fields.Char("Checksum", copy=False)

    standby_delivery = fields.Boolean(
        string="Standby Delivery",
        store=False,
        compute="_compute_standby_delivery",
        search="_search_standby_delivery",
    )

    def _get_delivery_partners_for_partners(self):
        delivery_partners = {}
        for picking in self:
            partner = picking.partner_id
            if partner and partner not in delivery_partners:
                if partner.type == "contact" and partner.parent_id:
                    partner = partner.parent_id
                delivery_partners[picking.partner_id] = partner
        return delivery_partners

    @api.model
    def _get_candidate_picking(self):
        domain = [
            ("state", "=", "confirmed"),
            ("delivery_round_id", "=", False),
            ("partner_id", "!=", False),
            ("picking_type_id.subcode", "=", "PICK"),
        ]
        return self.search(domain)

    def _search_standby_delivery(self, operator, value):
        candidates = self._get_candidate_picking()
        ids = candidates.filtered("standby_delivery").ids
        result_operator = "in"
        if (not value and operator == "=") or (value and operator == "!="):
            result_operator = "not in"
        return [("id", result_operator, ids)]

    @api.model
    def _find_bypartners(self, partner_ids):
        query_find_by_partners = """
SELECT id
FROM res_partner
WHERE id in %s AND
    EXISTS (SELECT instance.id
    FROM round_instance_round_itinerary_rel AS rel
      INNER JOIN round_instance AS instance
        ON rel.round_instance_id = instance.id
      INNER JOIN round_itinerary_position AS position
        ON position.itinerary_id = rel.round_itinerary_id
      INNER JOIN res_partner
        ON position.partner_id = res_partner.id
      LEFT JOIN round_instance_round_tag_rel AS instance_tag
        ON instance.id = instance_tag.round_instance_id
      LEFT JOIN round_itinerary_position_round_tag_rel AS customer_tag
        ON position.id = customer_tag.round_itinerary_position_id
    WHERE instance.state = 'draft'
      AND (instance_tag.round_tag_id = customer_tag.round_tag_id
          OR customer_tag IS NULL
          OR instance_tag IS NULL)
    ORDER BY instance.date ASC, instance.time_picking_planned ASC
    LIMIT 1);
"""
        self.env.cr.execute(query_find_by_partners, (tuple(partner_ids),))
        return [r[0] for r in self.env.cr.fetchall()]

    @api.model
    def _find_bypartners_geo(self, partner_ids):
        # coupled to _find_bypartners from the alc_geo_delivery_rounds module
        if not partner_ids:
            return []
        query = """
SELECT res_partner.id
FROM
    res_partner
WHERE id in %s AND EXISTS (
    SELECT
        ri.id
    FROM
        res_partner_round_tag_rel, round_instance_round_tag_rel,
        round_template AS rt JOIN round_instance AS ri ON ri.template_id = rt.id
    WHERE
        ri.state = 'draft'
        AND ST_Contains(rt.geo_polygon_shape, ST_AsEWKT(res_partner.geo_point))
        AND (NOT EXISTS (
                SELECT round_tag_id
                FROM res_partner_round_tag_rel
                WHERE res_partner_id = res_partner.id
                )
            OR EXISTS (
                SELECT round_instance_id
                FROM
                    res_partner_round_tag_rel AS pr JOIN
                    round_instance_round_tag_rel AS rr
                    ON pr.round_tag_id = rr.round_tag_id
                WHERE res_partner_id = res_partner.id AND round_instance_id = ri.id
                LIMIT 1
            )
        )
    LIMIT 1);
"""
        self.env.cr.execute(query, (tuple(partner_ids),))
        return [r[0] for r in self.env.cr.fetchall()]

    @api.depends("state", "delivery_round_id", "partner_id", "picking_type_subcode")
    def _compute_standby_delivery(self):
        partners_mapping = self._get_delivery_partners_for_partners()
        partners = self.env["res.partner"]
        for p in partners_mapping:
            partners |= p
        ps_dynamic = partners.filtered(lambda p: not p.not_in_dynamic_delivery_round)
        ps_dyn_del = self._find_bypartners_geo(ps_dynamic.ids) if ps_dynamic else []
        rest = partners.filtered(lambda p: p.id not in ps_dyn_del)
        ps_sta_del = self._find_bypartners(rest.ids) if rest else []
        pids = ps_sta_del + ps_dyn_del
        for p in self:
            p.standby_delivery = (
                p.state == "confirmed"
                and p.picking_type_subcode == "PICK"
                and not p.delivery_round_id
                and p.partner_id
                and partners_mapping[p.partner_id].id in pids
            )
