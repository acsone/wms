# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Keycloak",
    "description": """Alcyon Keycloak""",
    "version": "16.0.1.0.4",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Alcyon
        "alc_elasticsearch_security_loyalty",
        "alc_elasticsearch_security_vt_groups",
        "alc_eshop_ordering_allowed",
        "alc_partner_pricelist",
        "connector_keycloak",
        # Alcyon/Delivery
        "alc_shipping_fee",
    ],
    "application": False,
    "data": [],
    "demo": [],
    "development_status": "Alpha",
}
