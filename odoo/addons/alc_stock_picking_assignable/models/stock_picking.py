# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS


class StockPicking(models.Model):

    _inherit = "stock.picking"

    is_assignable = fields.Boolean(
        compute="_compute_is_assignable", search="_search_is_assignable",
    )

    @api.depends(
        "picking_type_subcode", "printed", "pack_operation_product_ids",
    )
    def _compute_is_assignable(self):
        for picking in self:
            not_assignable = (
                picking.picking_type_subcode != "PICK"
                or picking.state in ("done", "cancel")
                or (picking.printed and picking.pack_operation_product_ids)
            )
            picking.is_assignable = not not_assignable

    @api.model
    def _get_is_assignable_domain(self):
        domain = [
            ("picking_type_subcode", "=", "PICK"),
            ("state", "not in", ("done", "cancel")),
            ("printed", "=", False),
        ]
        return domain

    @api.model
    def _search_is_assignable(self, operator, value):
        if "in" in operator:
            raise ValueError("Invalid operator %s" % operator)
        search_is_assignable = (
            # is_assignable != False
            (operator in NEGATIVE_TERM_OPERATORS and not value)
            or
            # is_assignable = True
            (operator not in NEGATIVE_TERM_OPERATORS and value)
        )
        domain = self._get_is_assignable_domain()
        ids = self.search(domain).ids
        operator = "in"
        if not search_is_assignable:
            operator = "not in"
        return [("id", operator, ids)]
