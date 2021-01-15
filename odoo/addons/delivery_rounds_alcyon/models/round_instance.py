# -*- coding: utf-8 -*-
# © 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RoundInstance(models.Model):
    _inherit = "round.instance"

    count_picking_available_total_ali = fields.Integer(
        "Picking Available Total Aliment",
        compute="_compute_count_picking",
        readonly=True,
    )
    count_picking_done_total_ali = fields.Integer(
        "Picking Done Total Aliment", compute="_compute_count_picking", readonly=True
    )
    count_picking_available_total_med = fields.Integer(
        "Picking Available Total Medicament",
        compute="_compute_count_picking",
        readonly=True,
    )
    count_picking_done_total_med = fields.Integer(
        "Picking Done Total Medicament", compute="_compute_count_picking", readonly=True
    )
    count_picking_available_total_frigo = fields.Integer(
        "Picking Available Total Frigo", compute="_compute_count_picking", readonly=True
    )
    count_picking_done_total_frigo = fields.Integer(
        "Picking Done Total Frigo", compute="_compute_count_picking", readonly=True
    )
    count_picking_available_total_mat = fields.Integer(
        "Picking Available Total Materiel",
        compute="_compute_count_picking",
        readonly=True,
    )
    count_picking_done_total_mat = fields.Integer(
        "Picking Done Total Materiel", compute="_compute_count_picking", readonly=True
    )
    count_picking_available_total_pharm = fields.Integer(
        "Picking Available Total Pharmacie",
        compute="_compute_count_picking",
        readonly=True,
    )
    count_picking_done_total_pharm = fields.Integer(
        "Picking Done Total Pharmacie", compute="_compute_count_picking", readonly=True
    )

    @api.depends("picking_ids")
    def _compute_count_picking(self):
        query = """
            SELECT p.delivery_round_id, z.code,
            count(*) AS total,
            count(*) FILTER (WHERE p.state='done') AS done
            FROM stock_picking p
            LEFT JOIN stock_picking_type t ON p.picking_type_id = t.id
            LEFT JOIN picking_zone z ON t.picking_zone_id = z.id
            WHERE
            -- p.state is done if no stock moves (all sent to backorder)
            (p.state in ('partially_available', 'assigned', 'done') OR EXISTS (
              SELECT id FROM stock_move
              WHERE stock_move.picking_id = p.id
              AND (stock_move.state in ('done', 'assigned')
                OR (stock_move.state = 'confirmed'
                  AND stock_move.partially_available))))
            AND p.picking_type_subcode='PICK'
            AND p.delivery_round_id in %s
            GROUP BY p.delivery_round_id, z.code
        """
        self._cr.execute(query, (tuple(self.ids),))

        picking_total = {}.fromkeys(self.ids, 0)
        picking_done = {}.fromkeys(self.ids, 0)

        for delivery_round_id, code, total, done in self._cr.fetchall():
            rec = self.browse(delivery_round_id)

            if code == "01":
                rec.count_picking_available_total_med = total
                rec.count_picking_done_total_med = done
            elif code == "02":
                rec.count_picking_available_total_mat = total
                rec.count_picking_done_total_mat = done
            elif code == "03":
                rec.count_picking_available_total_frigo = total
                rec.count_picking_done_total_frigo = done
            elif code == "04":
                rec.count_picking_available_total_ali = total
                rec.count_picking_done_total_ali = done
            elif code == "05":
                rec.count_picking_available_total_pharm = total
                rec.count_picking_done_total_pharm = done

            picking_total[rec.id] += total
            picking_done[rec.id] += done

        for rec in self:
            rec.count_picking_available_total = picking_total[rec.id]
            rec.count_picking_done_total = picking_done[rec.id]

        query = """
            SELECT p.delivery_round_id, count(distinct partner_id)
            FROM stock_picking p
            WHERE EXISTS (
              SELECT id FROM stock_move
              WHERE stock_move.picking_id = p.id
              AND (stock_move.state in ('done', 'assigned')
                OR (stock_move.state = 'confirmed'
                  AND stock_move.partially_available)))
            AND p.delivery_round_id in %s
            GROUP BY p.delivery_round_id
        """
        self._cr.execute(query, (tuple(self.ids),))
        for delivery_round_id, count in self._cr.fetchall():
            rec = self.browse(delivery_round_id)
            rec.count_picking_available_partner = count
