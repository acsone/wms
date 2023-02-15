# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductProduct(models.Model):

    _inherit = "product.product"

    older_lot_id = fields.Many2one(
        "stock.production.lot", string="Older lot", compute="_compute_older_lot_id"
    )

    best_before_date = fields.Date(compute="_compute_best_before_date")

    def _compute_older_lot_id(self):
        """Find the active lot with the oldest expirtation date.

        The lot must be in a physical location, not scraped not reserved and still have
        some quantity.

        """
        tracked_product_ids = self.filtered(lambda p: p.tracking == "lot").ids
        lot_id_by_product_id = {}
        if tracked_product_ids:
            location_physical = self.env.ref("alc_stock_location_data.stock_location_vlb")
            get_lot_query = """
                SELECT
                    DISTINCT ON (product_id) product_id,
                    id
                FROM
                    stock_production_lot as lot
                WHERE
                    lot.product_id in %s
                    AND lot.life_date > now()
                    AND EXISTS (
                        SELECT 1 FROM stock_quant AS quant
                            LEFT JOIN stock_location AS location
                                ON quant.location_id = location.id
                            WHERE quant.lot_id = lot.id AND
                                  location.parent_left > %s AND
                                  location.parent_right < %s AND
                                  location.scrap_location = FALSE AND
                                  quant.reservation_id is null AND
                                  quant.qty > 0)
                ORDER BY product_id,life_date
            """
            self.env.cr.execute(
                get_lot_query,
                (
                    tuple(tracked_product_ids),
                    location_physical.parent_left,
                    location_physical.parent_right,
                ),
            )
            lot_id_by_product_id = dict(self.env.cr.fetchall())
        for product in self:
            product.older_lot_id = lot_id_by_product_id.get(product.id)

    def _compute_best_before_date(self):
        for rec in self:
            life_date = rec.older_lot_id.life_date
            rec.best_before_date = life_date[:10] if life_date else None
