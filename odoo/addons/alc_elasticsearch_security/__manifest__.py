# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Elasticsearch Security pricelist",
    "description": """Compute Alcyon-specific ElasticSearch pricelist roles.""",
    "version": "16.0.2.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_partner_pricelist",
        "alc_partner_type",
        "alc_pricelist_role_name",
        "elasticsearch_security_mixin",
        # fmt: on
    ],
    "application": False,
    "data": ["views/se_backend.xml"],
    "demo": [],
}
