# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Specifc Helpdesk for Alcyon',
 'version': '10.0.1.0.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Helpdesk',
 'depends': [
     'account',
     'helpdesk',
     'mrp',
     'product',
     'specific_purchase',
     'stock',
 ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'data/helpdesk.xml',
     'security/ir.model.access.csv',
     'views/helpdesk.xml',
     'views/stock_picking.xml',
 ],
 'installable': True,
 }
