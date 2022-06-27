# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from psycopg2.extensions import AsIs

from odoo import api, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    def assign_operator(self):
        res = super(StockPicking, self).assign_operator()
        self._check_all_zones_launch_pickings()
        return res

    def _check_all_zones_launch_pickings(self):
        delivery_rounds = self.mapped("delivery_round_id")
        zones_todo_by_delivery_round = self._get_open_zones_by_delivery_round(
            delivery_rounds
        )
        for delivery_round in delivery_rounds:
            zones_todo = zones_todo_by_delivery_round.get(delivery_round.id)
            if delivery_round.auto_close_picking_launched:
                if zones_todo:
                    self._check_picking_launched_closing(delivery_round, zones_todo)
                else:
                    delivery_round.write({"picking_launched": False})

    def _check_picking_launched_closing(self, delivery_round, zones_todo):
        to_write = {}
        if "02" not in zones_todo:
            to_write["picking_mat_launched"] = False
        if "03" not in zones_todo:
            to_write["picking_frigo_launched"] = False
        if "04" not in zones_todo:
            to_write["picking_ali_launched"] = False
        if "05" not in zones_todo:
            to_write["picking_med_launched"] = False

        if to_write:
            delivery_round.write(to_write)

    @api.model
    def _get_open_zones_by_delivery_round(self, delivery_rounds):
        query = """
            SELECT
                sp.delivery_round_id,
                array_agg(distinct(pz.code))
            FROM
                stock_picking sp
                JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
                JOIN picking_zone pz ON pz.id = spt.picking_zone_id
            WHERE
                sp.picking_type_subcode='PICK'
                AND sp.printed is false
                %(delivery_round_ids)s
                AND (sp.state in ('partially_available', 'assigned', 'done') OR EXISTS (
                SELECT id FROM stock_move sm
                WHERE sm.picking_id = sp.id
                AND (sm.state in ('done', 'assigned')
                    OR (sm.state = 'confirmed'
                    AND sm.partially_available))))
            GROUP BY sp.delivery_round_id
        """
        args = {"delivery_round_ids": self._get_delivery_round_ids(delivery_rounds)}
        self.env.cr.execute(query, args)
        rows = self.env.cr.fetchall()
        result = defaultdict(list)
        for row in rows:
            result[row[0]] = row[1]
        return result

    def _get_delivery_round_ids(self, delivery_rounds):
        if delivery_rounds.ids and len(delivery_rounds.ids) > 1:
            ids = AsIs(
                "AND sp.delivery_round_id in {}".format(tuple(delivery_rounds.ids))
            )
        elif delivery_rounds.ids and len(delivery_rounds.ids) == 1:
            ids = AsIs("AND sp.delivery_round_id = {}".format(delivery_rounds.ids[0]))
        else:
            ids = AsIs("")
        return ids
