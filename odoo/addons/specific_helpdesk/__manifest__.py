# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Specific Helpdesk for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "OEEL-1",
    "category": "Helpdesk",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # helpdesk is an Odoo enterprise module
    "depends": [
        "account",
        "helpdesk",
        "purchase",
        "sale",
        "stock",
        "stock_receive_lot",
        "alc_supplier_purchase_manager",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        "data/helpdesk.stage.csv",
        "data/helpdesk.team.csv",
        "data/helpdesk_ticket_reason.xml",
        "data/mail_template.xml",
        "security/ir.model.access.csv",
        "wizards/create_helpdesk_ticket.xml",
        "wizards/stock_pack_operation_lot_add.xml",
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
