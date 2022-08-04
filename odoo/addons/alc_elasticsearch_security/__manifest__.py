# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Elasticsearch Security",
    "description": """Compute Alcyon-specific ElasticSearch roles.""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "alc_search_engine",
        "elasticsearch_security_mixin",
        "alc_partner_type",
        "pricelist_role_name",
        "alc_eshop_ads_elasticsearch",
        "alc_eshop_info_banner_elasticsearch",
        "shopinvader_url_locales",
    ],
    "application": False,
    "data": [
        "data/elasticsearch_backend.xml",
        "data/elasticsearch_role.xml",
        "views/se_backend_elasticsearch.xml",
    ],
    "demo": [],
}
