# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    life_date = fields.Datetime(string="Expiration Date", required=True)
    is_archived = fields.Boolean("Archived", default=False, readonly=True)

    @api.model
    def create(self, vals):
        new_vals = vals.copy()
        if not vals.get("life_date"):
            context = self.env.context or {}
            if context.get("default_life_date_allowed"):
                new_vals["life_date"] = fields.datetime.now()
        result = super(StockProductionLot, self).create(new_vals)
        return result

    @api.onchange("product_id")
    def _onchange_product(self):
        # Override the product_expiry module method
        # Do nothing : on Alcyon, the life_date is entered by user
        # and is not computed with production lot created date
        pass

    
