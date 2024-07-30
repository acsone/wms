# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "Stock Receive Wizard",
    "version": "16.0.1.0.0",
    "author": "BCIM, ACSONE SA/NV",
    "maintainer": "Camptocamp",
    "license": "LGPL-3",  # MUST BE LGPL since will be mixed with helpdesk OEEL
    "category": "Stock Management",
    "depends": [
        # Custom
        "alc_stock_lot_track_food",
        # OCA
        "stock_picking_is_completed",
        # Others
        "product_expiry",
    ],  # LGPL
    "data": [
        "security/alc_stock_receive_lot.xml",
        "views/stock_location.xml",
        "wizards/stock_pack_operation_lot_add.xml",
        "views/stock_picking.xml",
    ],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
