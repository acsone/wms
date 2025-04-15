# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Search Engine Loyalty",
    "description": """
        Export loyalty programs to the search engine""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Third-party
        "connector_search_engine",
        "loyalty_initial_date_validity",
        "queue_job_cron",
        "search_engine_serializer_pydantic",
        # Alcyon
        "alc_eshop_search_engine_temporal_info_mixin",
    ],
    "data": [
        "views/loyalty_program_view.xml",
        "views/se_backend.xml",
        "data/ir_cron.xml",
        "data/se_index.xml",
    ],
    "demo": [],
    "development_status": "Alpha",
    "additional_dependencies": {
        "python": ["extendable-pydantic"],
    },
}
