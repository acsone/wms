# Copyright 2017 Julien Coux (Camptocamp)
# Copyright 2017 Sylvain Van Hoof (Okia SPRL)
# Copyright 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product additional for Alcyon",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Custom
        "alc_additional_product_base",
        # OCA
        "stock_move_propagate_first_move",
        "stock_move_propagate_first_move_cancel",
        # Others
        "sale_stock",
    ],
    "data": [
        "views/stock_picking_type.xml",
    ],
    "installable": True,
}
