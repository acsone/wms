# -*- coding: utf-8 -*-
# Copyright 2020 Acsone SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from psycopg2.extensions import AsIs

from odoo import fields, models
from odoo.osv.expression import NEGATIVE_TERM_OPERATORS


class StockQuantPackage(models.Model):
    _inherit = "stock.quant.package"

    nbr_packages = fields.Integer("Number of packages", default=1)
    original_picking_zone_id = fields.Many2one("picking.zone", "Original picking zone")

    def _search_location(self, operator, value):
        quant_with_parent_ids = []
        quant_ids = []
        if value:
            op = "JOIN" if operator not in NEGATIVE_TERM_OPERATORS else "LEFT JOIN"
            query = """
               SELECT
                    stock_quant_package.id,
                    parent_id
                FROM
                    stock_quant_package
                    %s stock_quant on stock_quant.package_id = stock_quant_package.id
                WHERE
                    location_id = %s;
                """
            params = (AsIs(op), value)
        else:  # ('location_id', '=', False) ('location_id', '!=', False)
            op = "JOIN" if operator in NEGATIVE_TERM_OPERATORS else "LEFT JOIN"
            query = """
               SELECT
                    stock_quant_package.id,
                    parent_id
                FROM
                    stock_quant_package
                    %s stock_quant on stock_quant.package_id = stock_quant_package.id
                WHERE
                    package_id is null;
                """
            params = (AsIs(op),)
        self.env.cr.execute(query, params)
        for quant_id, parent_id in self.env.cr.fetchall():
            if parent_id:
                quant_with_parent_ids.append(quant_id)
            else:
                quant_ids.append(quant_id)
        if quant_with_parent_ids:
            quant_ids.extend(
                self.search([("id", "parent_of", quant_with_parent_ids)]).ids
            )
        if quant_ids:
            return [("id", "in", quant_ids)]
        else:
            return [("id", "=", False)]
