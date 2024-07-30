# Copyright 2017 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Specific Helpdesk for Alcyon",
    "version": "16.0.1.0.0",
    "author": "Camptocamp, ACSONE SA/NV",
    "license": "Other proprietary",
    "category": "Helpdesk",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # helpdesk is an Odoo enterprise module
    "depends": [
        # Custom
        "alc_stock_receive_lot",
        "alc_supplier_purchase_manager",
        # Others
        "account",
        "helpdesk",
        "purchase",
        "sale",
        "stock",
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
        "views/res_partner_views.xml",
        "views/helpdesk_views.xml",
        "views/purchase_order_views.xml",
        "views/sale_order_views.xml",
        "views/account_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
        "data/ticket_sequence.xml",
    ],
    "installable": True,
    "external_dependencies": {"python": ["openupgradelib"]},
}
