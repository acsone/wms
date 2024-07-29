# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Documents Prices",
    "description": """Alcyon Documents Prices""",
    "version": "16.0.1.0.3",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_documents",
        "alc_product_flattened_data",
        # OCA
        "fs_attachment",
        # fmt: on
    ],
    "data": ["data/ir_config_parameter.xml", "data/queue_job_function.xml"],
    "demo": [],
    "external_dependencies": {"python": ["unicodecsv"]},
    "installable": True,
}
