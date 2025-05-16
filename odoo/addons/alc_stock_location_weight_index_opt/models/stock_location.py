# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields
from odoo.osv.expression import AND
from odoo.tools.query import Query

from odoo.addons.stock.models.stock_location import Location


class StockLocation(Location):
    outgoing_move_line_ids = fields.One2many(
        compute="_compute_move_line_ids",
        search="_search_outgoing_move_line_ids",
        store=False,
    )
    incoming_move_line_ids = fields.One2many(
        compute="_compute_move_line_ids",
        search="_search_incoming_move_line_ids",
        store=False,
    )

    def _compute_move_line_ids(self):
        base_domain = [("state", "not in", ["draft", "done", "cancel"])]
        sml_model = self.env["stock.move.line"]
        for rec in self:
            if rec.usage != "internal":
                rec.incoming_move_line_ids = False
                rec.outgoing_move_line_ids = False
                continue
            rec.incoming_move_line_ids = sml_model.search(
                AND([[("location_dest_id", "=", rec.id)], base_domain]),
            )
            rec.outgoing_move_line_ids = sml_model.search(
                AND([[("location_id", "=", rec.id)], base_domain]),
            )

    @api.model
    def _search_outgoing_move_line_ids(self, operator, value):
        return self._search_move_line_ids("location_id", operator, value)

    @api.model
    def _search_incoming_move_line_ids(self, operator, value):
        return self._search_move_line_ids("location_dest_id", operator, value)

    def _search_move_line_ids(self, field, operator, value):
        base_domain = [
            ("state", "not in", ["draft", "done", "cancel"]),
            (f"{field}.usage", "=", "internal"),
        ]
        if isinstance(value, bool) and (
            (not value and operator == "=") or value and operator == "!="
        ):
            grouped = self.env["stock.move.line"].read_group(
                base_domain, fields=[field], groupby=[field]
            )
            location_ids = [g[field][0] for g in grouped if g[field]]
            return [("id", "not in", location_ids)]
        domain = []
        if isinstance(value, Query):
            query_str, params = value.select()
            self.env.cr.execute(query_str, params)
            ids = [row[0] for row in self.env.cr.fetchall()]
            domain = [("id", "in", ids)]
        elif isinstance(value, list):
            domain = [("id", operator, value)]

        domain = AND([base_domain, domain])
        grouped = self.env["stock.move.line"].read_group(
            domain, fields=[field], groupby=[field]
        )
        location_ids = [g[field][0] for g in grouped if g[field]]
        return [("id", "in", location_ids)]
