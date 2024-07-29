# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Sale Cart Info",
    "description": """Alcyon: Manage client reference on sale_cart and note on sale_order""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_eshop_ordering_allowed",
        "alc_partner_type",
        "alc_product_pharmacy",
        "alc_sale_suite_name",
        # OCA
        "shopinvader_api_cart",
        "shopinvader_schema_sale",
        # fmt: on
    ],
    "data": [
        "data/mail_template.xml",
    ],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
    "pre_init_hook": "pre_init_hook",
}
