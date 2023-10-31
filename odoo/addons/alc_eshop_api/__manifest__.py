# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Api",
    "description": """
        Alcyon: Eshop api""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "fastapi",
        "shopinvader_api_address",
        "shopinvader_api_cart",
        "shopinvader_fastapi_auth_jwt",
        "shopinvader_restapi",
        "shopinvader_restapi_auth_jwt",
        "alc_eshop_api_sale_statistic",
        "alc_eshop_api_classifieds",
        "alc_eshop_api_cms",
        "alc_eshop_api_registration",
        "alc_eshop_api_documents",
        "alc_eshop_api_catalog",
        "alc_eshop_api_discounts",
        "alc_eshop_api_products_on_order",
        "alc_eshop_api_veterinary_groups",
        "alc_eshop_api_promotion_subscriptions",
        "alc_eshop_api_forms",
    ],
    "data": [
        "views/fastapi_endpoint.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
}
