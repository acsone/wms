# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010 OpenERP s.a. (<http://openerp.com>).
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
    "name": "Web Auto Refresh Views",
    "summary": "This module use the auto_refresh field of OpenERP actions to "
    "set a time based refresh of views used on the actions.",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "category": "web",
    "author": "aekroft@gmail.com",
    "contributor": "Jacques-Etienne Baudoux <je@bcim.be>",
    "website": "www.soltein.org",
    "depends": [
        "web",
        # 'web_calendar', 'web_graph', 'web_kanban',
    ],
    "data": ["assets.xml"],
    "installable": True,
}
