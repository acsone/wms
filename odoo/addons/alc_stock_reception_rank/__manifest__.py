# © 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Stock Reception Priority",
    "version": "16.0.1.0.1",
    "author": "BCIM, ACSONE SA/NV",
    "maintainer": "ACSONE SA/NV",
    "category": "Stock Management",
    "depends": [
        # Odoo Community
        "stock",
        # Third-party
        "stock_available_immediately",
        "stock_available_to_promise_release",
        "stock_grn",
        "stock_move_propagate_first_move",
        "stock_picking_start",
        "stock_release_channel",
        # Alcyon/Stock Management
        "alc_stock_picking_rank",
    ],
    "data": [
        "views/stock_picking.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
