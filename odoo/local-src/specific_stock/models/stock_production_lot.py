# -*- coding: utf-8 -*-
# © 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import math
import random

from openerp import models, fields, api
from openerp.exceptions import Warning


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    life_date = fields.Datetime(
        string='End of Life Date',
        required=True,
    )
    is_archived = fields.Boolean('Archived', default=False, readonly=True)
    checksum = fields.Char('Checksum', readonly=True)

    # Cancel defaults values from `product_expiry` module
    _defaults = {
        'life_date': None,
        'use_date': None,
        'removal_date': None,
        'alert_date': None,
    }

    @api.model
    def create(self, vals):
        new_vals = vals.copy()
        if 'life_date' not in vals.keys():
            context = self.env.context or {}
            if context.get('default_life_date_allowed'):
                new_vals['life_date'] = fields.datetime.now()
        result = super(StockProductionLot, self).create(new_vals)

        if 'checksum' not in vals:
            result.compute_checksum()

        return result

    @api.onchange('product_id')
    def _onchange_product(self):
        # Override the product_expiry module method
        # Do nothing : on Alcyon, the life_date is entered by user
        # and is not computed with production lot created date
        pass

    @api.multi
    @api.depends('product_id')
    def compute_checksum(self):
        lot_checksum_size = int(self.env['ir.config_parameter']. \
                                get_param('lot_checksum_size', 3))
        same_lot_checksum_range = int(self.env['ir.config_parameter']. \
                                      get_param('lot_checksum_size', 2))

        number_of_element = int(math.pow(10, lot_checksum_size)) - 1

        for lot in self:
            product = lot.product_id
            if not product or lot.checksum:
                continue

            checksum_not_available = set()
            location_to_skip = set()
            for stock_bin in product.stock_bin_ids:
                location = stock_bin.bin_location_id

                if not location.is_valid_location:
                    continue

                # To improve this method we keep previous computed shelves
                zone = location.zone
                corridor = location.corridor
                shelve = location.shelve
                if (zone, corridor, shelve) in location_to_skip:
                    continue
                else:
                    location_to_skip.add((zone, corridor, shelve))

                shelves = []
                shelve_code = ord(shelve)
                min_shelve_code = shelve_code - same_lot_checksum_range
                max_shelve_code = shelve_code + same_lot_checksum_range
                for code in range(min_shelve_code, max_shelve_code):
                    if code < ord('1') \
                            or (ord('9') < code < ord('A')) \
                            or code > ord('Z'):
                        continue
                    shelves.append(unichr(code))

                not_available_checksum_query = """
                SELECT DISTINCT lot.checksum
                FROM stock_production_lot AS lot
                WHERE lot.product_id IN (
                  SELECT stock_bin.product_id
                  FROM product_stock_bin AS stock_bin
                  WHERE stock_bin.location_id IN (
                    SELECT location.id
                    FROM stock_location AS location
                    WHERE location.zone = %s
                    AND location.corridor = %s
                    AND location.shelve IN %s)
                  )
                AND (lot.is_archived = FALSE OR lot.is_archived IS NULL);
                """
                self.env.cr.execute(not_available_checksum_query,
                                    (location.zone,
                                     location.corridor,
                                     tuple(shelves)))
                for result in self.env.cr.fetchall():
                    checksum_not_available.add(result[0])

            if len(checksum_not_available) == number_of_element:
                raise Warning('There is no checksum available')

            checksum = None
            while not checksum:
                new_checksum = format(random.randint(1, number_of_element),
                                      '0%d' % lot_checksum_size)
                if new_checksum in checksum_not_available:
                    continue
                checksum = new_checksum

            if checksum:
                lot.checksum = checksum

    @api.model
    def archive_lots(self):
        location_customers = self.env.ref('stock.stock_location_customers')

        query = """
            SELECT lot.id
            FROM stock_production_lot AS lot
            WHERE lot.is_archived = FALSE
            AND EXISTS (SELECT 1
                          FROM stock_production_lot AS next_lot
                          WHERE next_lot.product_id = lot.product_id
                          AND next_lot.life_date >= lot.life_date
                          AND next_lot.id <> lot.id
                          AND next_lot.active = TRUE)
            AND NOT EXISTS (SELECT 1
                            FROM stock_quant AS quant
                            WHERE quant.lot_id = lot.id
                            AND quant.location_id <> %s);
            """
        self.env.cr.execute(query, (location_customers.id,))

        result = self.env.cr.fetchall()
        lot_to_archive_ids = [lot[0] for lot in result]

        self.browse(lot_to_archive_ids).write({
            'is_archived': True,
        })
