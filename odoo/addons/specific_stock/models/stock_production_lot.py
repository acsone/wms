# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    life_date = fields.Datetime(string="Expiration Date", required=True)
    is_archived = fields.Boolean("Archived", default=False, readonly=True)
    product_id = fields.Many2one(index=True)

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

    @api.model
    def archive_lots(self):
        """
        A product can have a lot of lots. After a short period all checksum
        can be used in a range. To avoid this problem we archive old lot.
        Archive a lot has not effect (we not use the field active)
        but if a lot is archived it'll not be used to compute other checksum.

        We archive a lot if and only if:
        - There are no more products in this lot
        - There is a new lot (with a higher expiration date) for this product
        :return:
        """

        query = """
            SELECT lot.id
            FROM stock_production_lot AS lot
            WHERE lot.is_archived = FALSE
            AND EXISTS (SELECT 1
                          FROM stock_production_lot AS next_lot
                          WHERE next_lot.product_id = lot.product_id
                          AND next_lot.life_date >= lot.life_date
                          AND next_lot.id <> lot.id)
            AND NOT EXISTS (SELECT 1
                            FROM stock_quant AS quant
                            JOIN stock_location sl on sl.id = quant.location_id
                            WHERE quant.lot_id = lot.id AND sl.usage = 'internal'
                            AND (%s)
                            );
            """
        stock_locations = (
            self.env["stock.warehouse"].search([]).mapped("view_location_id")
        )
        w = []
        for loc in stock_locations:
            w.append(
                "sl.parent_left >= %s and sl.parent_right < %s"
                % (loc.parent_left, loc.parent_right)
            )
        or_query = " OR ".join(w)
        self.env.cr.execute(query, (AsIs(or_query),))

        result = self.env.cr.fetchall()
        lot_to_archive_ids = [lot[0] for lot in result]

        self.browse(lot_to_archive_ids).write({"is_archived": True})
