##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright (C) 2016 BCIM <http://www.bcim.be>
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
    "name": "Stock Lot Update",
    "version": "16.0.1.0.0",
    "category": "Stock Management",
    "author": "BCIM, ACSONE SA/NV",
    "depends": [
        # Others
        "stock",
    ],
    "data": [
        "security/stock_lot_update_groups.xml",
        "security/stock_lot_update_access.xml",
        "views/stock_lot.xml",
        "wizard/stock_lot_update.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "application": False,
    "pre_init_hook": "pre_init_hook",
}
