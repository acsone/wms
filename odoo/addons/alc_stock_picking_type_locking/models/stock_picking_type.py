# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPickingType(models.Model):

    _inherit = "stock.picking.type"

    def lock(self):
        """Takes an advisory lock for each picking type into the recordset"""
        for rec in self:
            self.env.cr.execute("SELECT pg_advisory_xact_lock(%s);", (rec.id,))
            self.env.cr.fetchone()[0]  # pylint: disable=expression-not-assigned
