# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Alc Stock Picking Priority Management",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV, Odoo Community Association (OCA)",
    "category": "stock",
    "depends": [
        # OCA
        "stock_available_to_promise_release",
        "stock_move_manage_priority",
    ],
    "website": "https://github.com/OCA/stock-logistics-workflow",
    "data": [
        "views/stock_picking_views.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
}
