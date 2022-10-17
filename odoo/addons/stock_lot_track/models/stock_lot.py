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
from odoo import fields

from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.product_expiry.models.production_lot import StockLot as StockLotBase


class StockLot(StockLotBase, extends=True):

    product_id = fields.Many2one[ProductProduct](tracking=True)
    name = fields.Char(tracking=True)

    use_date = fields.Datetime(tracking=True)
    removal_date = fields.Datetime(tracking=True)
    expiration_date = fields.Datetime(tracking=True)
    alert_date = fields.Datetime(tracking=True)
