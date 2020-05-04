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
from datetime import date

from odoo import api, fields, models

DEFAULT_BIN_CHECKSUM = "12"


class StockLocation(models.Model):
    _inherit = "stock.location"

    bin_checksum_1 = fields.Char("Checksum 1", default=DEFAULT_BIN_CHECKSUM)
    bin_checksum_2 = fields.Char("Checksum 2", default=DEFAULT_BIN_CHECKSUM)
    bin_checksum_3 = fields.Char("Checksum 3")

    @api.multi
    def get_checksum(self):
        """
        Return the checksum according the following rule:
        - even day : return checksum 1
        - odd day: return checksum 2

        The checksum 3 is not used but we need to keep it for the future

        Eg: 1 january => odd day => use the checksum 2
         2 january => even day => use the checksum 1
        :return:
        """

        is_odd_day = date.today().day % 2
        if is_odd_day:
            return self.bin_checksum_2
        else:
            return self.bin_checksum_1
