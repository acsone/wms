# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    product_ids = fields.Many2many('product.product', string='Products')

    @api.model
    def _selection_filter(self):
        result = super(StockInventory, self)._selection_filter()

        result.append(('products_selected', 'Products selected'))
        return result

    @api.multi
    def prepare_inventory(self):
        for inventory in self:
            if inventory.filter != 'products_selected' or inventory.line_ids:
                continue
            vals = {'state': 'confirm', 'date': fields.Datetime.now()}

            inventory_lines = inventory._get_inventory_lines_with_lots_values()
            lines_values = [
                (0, 0, line_values) for line_values in inventory_lines
            ]
            vals.update({'line_ids': lines_values})
            inventory.write(vals)
        return super(StockInventory, self).prepare_inventory()

    @api.multi
    def _get_inventory_lines_with_lots_values(self):
        self.ensure_one()

        locations = self.env['stock.location'].search(
            [('id', 'child_of', [self.location_id.id])]
        )

        vals = []
        Product = self.env['product.product']
        # Empty recordset of products available in stock_quants
        quant_products = self.env['product.product']

        if not self.product_ids:
            raise UserError(_('Please select at least one product'))

        query = """
          SELECT product_id,
            sum(qty) as product_qty,
            location_id,
            lot_id as prod_lot_id,
            package_id,
            owner_id as partner_id
          FROM stock_quant
          WHERE product_id IN %s
            AND location_id IN %s
          GROUP BY
           product_id,
           location_id,
           lot_id,
           package_id,
           partner_id"""
        self.env.cr.execute(
            query, (tuple(self.product_ids.ids), tuple(locations.ids))
        )

        for product_data in self.env.cr.dictfetchall():
            # replace the None the dictionary by False,
            # because falsy values are tested later on
            void_fields = [
                item[0] for item in product_data.items() if item[1] is None
            ]
            for void_field in void_fields:
                product_data[void_field] = False
            product_data['theoretical_qty'] = product_data['product_qty']
            if product_data['product_id']:
                product_data['product_uom_id'] = Product.browse(
                    product_data['product_id']
                ).uom_id.id
                quant_products |= Product.browse(product_data['product_id'])
            vals.append(product_data)

        # Add exhausted products
        exhausted_vals = self._get_empty_product_bin(
            self.product_ids, quant_products
        )
        vals.extend(exhausted_vals)

        return vals
