# -*- coding: utf-8 -*-
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class PutInPackHelper(models.TransientModel):
    _name = "put.in.pack.helper"

    nbr_packages = fields.Integer("Number of packages", required=True, default=1)
    picking_id = fields.Many2one("stock.picking", string="Picking", required=True)

    @api.multi
    def do_put_in_pack(self):
        self.ensure_one()

        package = self.picking_id.put_in_pack()
        if package:
            package.nbr_packages = self.nbr_packages
