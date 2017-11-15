# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{'name': 'Specific Helpdesk for Alcyon',
 'version': '10.0.1.0.0',
 'author': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Helpdesk',
 'depends': [
     'account',
     'helpdesk',
     'mrp_repair',
     'product',
     'purchase',
     'sale',
     'specific_purchase',
     'stock',
 ],
 'website': 'http://www.camptocamp.com',
 'data': [
     'security/ir.model.access.csv',
     'views/helpdesk.xml',
     'views/purchase_order.xml',
     'views/res_partner.xml',
     'views/sale_order.xml',
     'views/stock_picking.xml',
 ],
 'installable': True,
 }
