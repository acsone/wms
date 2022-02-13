# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon ElasticSearch",
    "description": """Alcyon Shopinvader ElasticSearch Configuration""",
    "version": "10.0.1.0.1",
    "author": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "license": "AGPL-3",
    "category": "alc",
    "depends": ["alc_eshop", "alc_partner_type", "alc_eshop_ads_elasticsearch"],
    "data": [
        "data/ir_export_category.xml",
        "data/ir_export_product.xml",
        "data/se_backend.xml",
        "data/se_index.xml",
        "data/shopinvader_backend.xml",
    ],
}
