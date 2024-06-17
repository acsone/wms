# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Elasticsearch Security Legacy Support",
    "description": """
        Temporary addon to support the renaming of role names into ES.
        Once the indexes are all updated, this addon can be removed.
        """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://www.acsone.eu",
    "depends": [
        "alc_elasticsearch_security",
        "alc_elasticsearch_security_vt_groups",
        "alc_pricelist_role_name",
        "alc_keycloak",
    ],
}
