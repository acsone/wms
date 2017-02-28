# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright 2016 BCIM sprl, DPHI sprl, Camptocamp
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

from odoo import models, fields


class ProductStockBin(models.Model):
    _name = 'product.stock.bin'
    _order = 'sequence'

    sequence = fields.Integer('Seq.')
    location_id = fields.Many2one(
        'stock.location', 'Location',
        required=True,
        ondelete='restrict')
    bin_location_id = fields.Many2one(
        'stock.location', 'Bin',
        required=True,
        ondelete='restrict')
    product_id = fields.Many2one(
        'product.template', 'Product',
        required=True,
        ondelete='cascade')


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_bin_ids = fields.One2many(
        'product.stock.bin', 'product_id', 'Stock Bins')
