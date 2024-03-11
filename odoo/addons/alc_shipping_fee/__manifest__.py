# Copyright 2017-2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Sipping Fee for Alcyon",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV, Camptocamp",
    "license": "AGPL-3",
    "category": "Delivery",
    "depends": [
        "delivery",
        "sale",
        "stock",
        "sale_stock",
        "stock_release_channel",
        "stock_release_channel_shipment_advice",
    ],
    "website": "https://www.acsone.eu",
    "data": [
        "views/delivery_carrier_views.xml",
        "views/stock_picking_type_views.xml",
        "views/sale_order_views.xml",
        "views/res_partner_views.xml",
    ],
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
