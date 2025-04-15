# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Elasticsearch Security: Loyalty",
    "description": """Compute Alcyon-specific Loyalty ElasticSearch roles.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Alcyon
        "alc_elasticsearch_security",
        "alc_eshop_search_engine_loyalty",
        "alc_loyalty_partner_applicability_cache",
    ],
    "application": False,
    "data": [],
    "demo": [],
    "post_init_hook": "post_init_hook",
    "external_dependencies": {"python": ["slugify"]},
    "development_status": "Alpha",
}
