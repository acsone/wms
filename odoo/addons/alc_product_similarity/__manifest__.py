# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Similarity Search",
    "description": """Alc Product Similarity Search""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Odoo Community
        "product",
        # Third-party
        "attribute_set",
        "field_vector",
        "product_multi_category",
        "queue_job",
        # Alcyon
        "alc_pim_product",
        "alc_product_animal_species",
        "alc_product_category_data",
        "alc_product_pharmacy",
        "alc_queue_job_background_channel",
    ],
    "application": False,
    "data": [
        "security/ir.model.access.csv",
    ],
    "demo": [],
    "external_dependencies": {"python": ["requests"]},
    "development_status": "Alpha",
    "pre_init_hook": "pre_init_hook",
}
