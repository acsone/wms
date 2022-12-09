# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


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
        picking_ids_with_stock = self._get_pickings_with_qty_avaible_in_stock()

        for p in self:
            p.standby_delivery = (
                partners_mapping[p.partner_id].id in pids
                and p.id in picking_ids_with_stock
            )

    @api.model
    def _get_pickings_with_qty_avaible_in_stock(self):
        # Get all location child of stock
        stock_location = self.env.ref("stock.stock_location_stock")
        customer_location = self.env.ref("stock.stock_location_customers")
        colis_souverain_id = self.env.ref(
            "alc_reception_pharmacy.product_colis_souverain"
        ).id

        # Get available stock for products on candidate pickings
        stock_query = """
        SELECT DISTINCT pp.id, SUM(sq.qty), array_agg(sp.id) FROM stock_picking sp
            JOIN stock_move sm ON sp.id = sm.picking_id
            JOIN product_product pp ON pp.id=sm.product_id
            JOIN stock_quant sq on sq.product_id=pp.id
            JOIN stock_location sl ON sl.id=sq.location_id
            JOIN stock_picking_type spt on spt.id=sp.picking_type_id
        WHERE sq.qty > 0 AND sq.reservation_id is null
            AND sl.scrap_location=false
            AND sl.parent_left > %(stock_parent_left)s
            AND sl.parent_right < %(stock_parent_right)s
            AND sp.state = 'confirmed'
            AND sp.delivery_round_id is null
            AND sp.partner_id is not null
            AND sm.state not in ('done', 'cancel')
            AND spt.subcode='PICK'
            AND pp.id != %(colis_souverain_id)s
        GROUP BY pp.id
        ORDER BY pp.id asc;

        """
        stock_args = {
            "stock_parent_left": stock_location.parent_left,
            "stock_parent_right": stock_location.parent_right,
            "colis_souverain_id": colis_souverain_id,
        }
        self.env.cr.execute(stock_query, stock_args)
        stock_by_product_id = {}
        picking_ids_by_product_id = {}
        for row in self.env.cr.fetchall():
            product_id = row[0]
            qty = row[1]
            ids = row[2]
            stock_by_product_id[product_id] = qty
            picking_ids_by_product_id[product_id] = ids

        # Check if out move exists for those products
        product_ids = stock_by_product_id.keys()
        move_out_query = """
        SELECT DISTINCT pp.id, SUM(sm.product_qty) FROM product_product pp
            JOIN stock_move sm on sm.product_id=pp.id
            JOIN stock_location sl on sl.id=sm.location_dest_id
        WHERE pp.id in %(product_ids)s
            AND sm.product_qty > 0
            AND sl.parent_left >= %(stock_parent_left)s
            AND sl.parent_right <= %(stock_parent_right)s
            AND sm.state not in ('done', 'cancel')
        GROUP BY pp.id
        ORDER BY pp.id ASC;
        """
        move_out_args = {
            "product_ids": tuple(product_ids),
            "stock_parent_left": customer_location.parent_left,
            "stock_parent_right": customer_location.parent_right,
        }
        self.env.cr.execute(move_out_query, move_out_args)
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        picking_ids = []
        move_out_result = self.env.cr.fetchall()
        # Difference between stock and out moves for those products
        # keep only products with positive quantities
        if move_out_result:
            for product_id, qty in move_out_result:
                initial_qty = stock_by_product_id.get(product_id, 0)
                remaining_qty = initial_qty - qty
                if float_compare(remaining_qty, 0, precision_digits=precision) > 0:
                    picking_ids += picking_ids_by_product_id.get(product_id, [])
        else:
            picking_ids = list(itertools.chain(*picking_ids_by_product_id.values()))

        return list(set(picking_ids))  # remove duplicate ids
