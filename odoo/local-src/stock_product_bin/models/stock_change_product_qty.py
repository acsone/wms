# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Sylvain Van Hoof <svh@sylvainvh.be>
#    Copyright (C) 2016
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, models, api


class StockChangeProductQty(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    stock_bin_ids = fields.One2many(
        'product.stock.bin', 'product_id', 'Stock Bins')

    @api.model
    def default_get(self, fields):
        result = super(StockChangeProductQty, self).default_get(fields)

        if self.env.context.get('active_model') != 'product.template' or \
                not self.env.context.get('active_id'):
            return result

        product_tmpl_id = self.env.context['active_id']
        if 'stock_bin_ids' in fields and result.get('product_id'):
            stock_bins = self.env['product.stock.bin'].search(
                [('product_id', '=', product_tmpl_id)])
            stock_bin_values = []
            for stock_bin in stock_bins:
                stock_bin_values.append([0, False, {
                    'product_id': stock_bin.product_id.id,
                    'sequence': stock_bin.sequence,
                    'location_id': stock_bin.location_id.id,
                    'bin_location_id': stock_bin.bin_location_id.id,
                }])

            result['stock_bin_ids'] = stock_bin_values

        return result

    @api.multi
    def change_product_qty(self):
        result = super(StockChangeProductQty, self).change_product_qty()

        for wizard in self:
            product_tmpl = wizard.product_tmpl_id
            product_tmpl.stock_bin_ids.unlink()
            for bin_tmp in wizard.stock_bin_ids:
                product_tmpl.stock_bin_ids.create({
                    'product_id': product_tmpl.id,
                    'sequence': bin_tmp.sequence,
                    'location_id': bin_tmp.location_id.id,
                    'bin_location_id': bin_tmp.bin_location_id.id,
                })

        return result

class ProductStockBinTemp(models.TransientModel):
    _inherit = 'product.stock.bin'
    _name = 'product.stock.bin.temp'

    wizard_id = fields.Many2one('product.stock.bin.temp', 'Wizard',
                                required=True)
