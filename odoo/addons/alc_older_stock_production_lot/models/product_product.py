# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields

from odoo.addons.product_expiry.models.product_product import Product as ProductBase
from odoo.addons.stock.models.stock_lot import StockLot


class ProductProduct(ProductBase):

    older_lot_id = fields.Many2one[StockLot](
        string="Older lot",
        compute="_compute_older_lot_id",
        search="_search_older_lot_id",
    )

    best_before_date = fields.Date(
        compute="_compute_best_before_date", string="Best before"
    )

    def _compute_older_lot_id(self):
        """Find the active lot with the oldest expiration date.

        The lot must be in a physical location, not scraped not reserved and still have
        some quantity.
        """
        tracked_product_ids = self.filtered(lambda p: p.tracking == "lot").ids
        lot_id_by_product_id = {}
        self.env["stock.lot"].invalidate_model(flush=True)
        self.env["stock.quant"].invalidate_model(flush=True)
        if tracked_product_ids:
            location_physical = self.env.ref(
                "alc_stock_location_data.stock_location_vlb"
            )
            get_lot_query = """
                SELECT
                    DISTINCT ON (product_id) product_id,
                    id
                FROM
                    stock_lot as lot
                WHERE
                    lot.product_id in %s
                    AND lot.expiration_date > now()
                    AND EXISTS (
                        SELECT 1 FROM stock_quant AS quant
                            LEFT JOIN stock_location AS location
                                ON quant.location_id = location.id
                            WHERE quant.lot_id = lot.id AND
                                  location.parent_path LIKE %s || '%%' AND
                                  location.scrap_location = FALSE AND
                                  quant.quantity - quant.reserved_quantity > 0)
                ORDER BY product_id,expiration_date
            """
            self.env.cr.execute(
                get_lot_query,
                (
                    tuple(tracked_product_ids),
                    location_physical.parent_path,
                ),
            )
            lot_id_by_product_id = dict(self.env.cr.fetchall())
        for product in self:
            product.older_lot_id = lot_id_by_product_id.get(product.id)

    def _search_older_lot_id(self, operator, value):
        lots = self.env["stock.lot"].search([("name", operator, value)])
        return [("older_lot_id", "in", lots)]

    @api.depends("older_lot_id", "older_lot_id.expiration_date")
    def _compute_best_before_date(self):
        for rec in self:
            expiration_date = rec.older_lot_id.expiration_date
            rec.best_before_date = expiration_date.date() if expiration_date else None
