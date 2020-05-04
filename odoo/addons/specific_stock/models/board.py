# -*- coding: utf-8 -*-
# Copyright 2019 Simone Orsi (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class Board(models.AbstractModel):
    _inherit = "board.board"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(Board, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        # FIX ALCYN-1950
        # make sure `custom_view_id` is always valued to avoid broken RPC call
        if res.get("custom_view_id") is None:
            res["custom_view_id"] = False
        return res
