# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright (C) 2015-TODAY BCIM <http://www.bcim.be>.
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

{
    "name": "Goods Received Note",
    "version": "10.0.1.0.3",
    "author": "BCIM",
    "maintainer": "QANSEE",
    "category": "Delivery",
    "complexity": "normal",
    "depends": ["stock", "alc_partner_carrier"],
    "website": "http://www.bcim.be/",
    "data": [
        "views/grn.xml",
        "views/stock_picking.xml",
        "views/stock_move.xml",
        "stock_sequence.xml",
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
    ],
    "tests": [],
    "installable": True,
    "auto_install": False,
    "license": "LGPL-3",
    "application": False,
}
