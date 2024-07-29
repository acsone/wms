# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Magento API Facade",
    "description": """Alcyon: Magento API Facade""",
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_eshop_api_cart",
        "alc_eshop_api_pickings",
        "alc_eshop_api_sale_statistic",
        "alc_partner_type",
        "alc_product_flattened_data",
        "alc_sale_channel",
        "alc_sale_order_date_order_short",
        "alc_sale_suite_name",
        "connector_keycloak",
        # OCA
        "jsonifier",
        "sale_cart",
        "sale_order_line_cancel",
        # fmt: on
    ],
    "demo": [],
    "external_dependencies": {"python": ["xmltodict", "dicttoxml"]},
    "installable": True,
    "development_status": "Alpha",
}
