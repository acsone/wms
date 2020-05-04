# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Specific Helpdesk for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "LGPL-3",
    "category": "Helpdesk",
    "depends": [
        "account",
        "helpdesk",  # Odoo enterprise module requires LGPL
        "mrp_repair",
        "product",
        "purchase",
        "sale",
        "specific_purchase",
        "stock",
        "stock_receive_lot",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        "data/helpdesk.stage.csv",
        "data/helpdesk.team.csv",
        "data/helpdesk_ticket_reason.xml",
        "data/mail_template.xml",
        "security/ir.model.access.csv",
        "wizards/create_helpdesk_ticket.xml",
        "wizards/stock_receive_lot.xml",
        "views/res_partner.xml",
        "views/helpdesk.xml",
        "views/purchase_order.xml",
        "views/sale_order.xml",
        "views/account_invoice.xml",
        "views/stock_picking.xml",
        "views/stock_move.xml",
        "data/ticket_sequence.xml",
    ],
    "installable": True,
}
