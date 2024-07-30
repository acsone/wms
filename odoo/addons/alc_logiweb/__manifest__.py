# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Logiweb",
    "description": """
        Alcyon: Logiweb connector""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_b2c_connector",
        "alc_b2c_connector_pricelist_discount",
        "alc_delivery_carrier_gls",
        "alc_partner_address",
        "alc_product_category_data",
        "alc_product_food",
        "alc_product_pricelist_data",
        # OCA
        "partner_manual_rank",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_filters.xml",
        "data/res_partner.xml",
        "data/sale_channel.xml",
        "data/alc_b2c_client.xml",
    ],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
