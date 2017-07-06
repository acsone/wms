# -*- coding: utf-8 -*-
# Copyright 2016 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random

from odoo import models, fields, api
from odoo.exceptions import Warning


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
        if not vals.get('life_date'):
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
        """
        This method will compute a checksum on each lot.
        A checksum on a lot has some constrains:
        - The size of the checksum should be 3 digits (can be changed)
        - The checksum cannot be equal to 000
        - A checksum cannot be use twice in a specific range
        (1 shelf on the left and 1 shelf on the right)

        To have the self next door we have to add 2 to the current shelf.

        A lot may be split in several bin. It's why we need to check all BIN
         to be sure that there no other lot with the same checksum.


         Steps to compute a checksum:
          1. Verify if the lot is linked to a location
          2. Compute the range of shelves
          3. Retrieve all checksum in this range (S-2/S+2)
          4. Compute a random checksum not used

        Example:
        We have a new lot (0000123)
        The lot will be split in two bin.
        - bin_1: GB2D11 (zone: G, corridor: B, shelf: 2, height: D, box: 11)
        - bin_2: GK6B06 (zone: G, corridor: K, shelf: 6, height: B, box: 06)

        For bin_1 and bin_2:
            (1) the location GB2D11 is correct
            (2) the range for the location GB2D11 is GB1 to GB4
            (3) there is 3 lots checksum in this range (023, 176, 939)
            _____
            (1') the location GK6B06 is correct
            (2') the range for the location GK6B06 is GK4 to GK8
            (3') there is 4 lots checksum in this range (032, 671, 002)

        (4) compute the checksum 028 not include in
        (023, 176, 939, 032, 671, 002)

        If there is not checksum available
        no checksum will be assigned to the lot
        :return:
        """
        lot_checksum_size = int(self.env['ir.config_parameter'].
                                get_param('lot_checksum_size', 3))
        same_lot_checksum_range = int(self.env['ir.config_parameter'].
                                      get_param('same_lot_checksum_range', 2))

        for lot in self:
            product = lot.product_id
            if not product or lot.checksum:
                continue

            checksum_not_available = set()
            location_to_skip = set()
            # We check all BINs
            for stock_bin in product.stock_bin_ids:
                location = stock_bin.bin_location_id

                # Step 1: Check the location
                if not location.is_valid_location:
                    continue

                zone = location.zone
                corridor = location.corridor
                shelf = location.shelf

                # Step 2: Compute the range of shelves
                # We can ignore this step if we are already
                # compute this location
                if (zone, corridor, shelf) in location_to_skip:
                    continue

                location_to_skip.add((zone, corridor, shelf))

                range_of_shelves = []

                try:
                    shelf_code = int(shelf)
                    is_letter = False
                except:
                    shelf_code = ord(shelf)
                    is_letter = True

                min_shelf_code = shelf_code - same_lot_checksum_range
                max_shelf_code = shelf_code + same_lot_checksum_range
                for code in (min_shelf_code, shelf_code, max_shelf_code):
                    if code < 1 \
                            or (9 < code < ord('A')) \
                            or code > ord('Z'):
                        continue

                    if is_letter:
                        code = unichr(code)
                    else:
                        code = format(code, '0%d' % 2)

                    range_of_shelves.append(code)

                # Step 3: Retrieve all lot checksum used in this shelf range
                not_available_checksum_query = """
                SELECT DISTINCT lot.checksum
                FROM stock_production_lot AS lot
                WHERE lot.product_id IN (
                  SELECT product_product.id
                  FROM product_product
                  WHERE product_product.product_tmpl_id IN (
                    SELECT stock_bin.product_id
                    FROM product_stock_bin AS stock_bin
                    WHERE stock_bin.bin_location_id IN (
                      SELECT location.id
                      FROM stock_location AS location
                      WHERE location.zone = %s
                      AND location.corridor = %s
                      AND location.shelf IN %s)
                    )
                  )
                AND (lot.is_archived = FALSE OR lot.is_archived IS NULL);
                """
                self.env.cr.execute(not_available_checksum_query,
                                    (location.zone,
                                     location.corridor,
                                     tuple(range_of_shelves)))
                for result in self.env.cr.fetchall():
                    if result[0]:
                        checksum_not_available.add(result[0])

            minval = 1
            maxval = 10 ** lot_checksum_size
            formated_checksum = [format(item, '0%d' % lot_checksum_size)
                                 for item
                                 in range(minval, maxval)]
            picklist = list(set(formated_checksum) -
                            set(checksum_not_available))
            if not picklist:
                raise Warning('There is no checksum available')

            # Step 4: Generate an available checksum
            checksum = random.choice(picklist)
            checksum_not_available.add(checksum)
            lot.checksum = checksum

    @api.model
    def archive_lots(self):
        """
        A product can have a lot of lots. After a short period all checksum
        can be used in a range. To avoid this problem we archive old lot.
        Archive a lot has not effect (we not use the field active)
        but if a lot is archived it'll not be used to compute other checksum.

        We archive a lot if and only if:
        - There are no more products in this lot
        - There is a new lot (with a higher life date) for this product
        :return:
        """
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
