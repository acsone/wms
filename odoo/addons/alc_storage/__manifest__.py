# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "ALC storage configuration",
    "description": """Alcyon: Adds Amazon S3 storage backend.""",
    "version": "10.0.1.0.0",
    "depends": [
        "server_environment_ir_config_parameter",
        "storage_backend_s3",
        "storage_thumbnail",
        "storage_image_product",
    ],
    "author": "ACSONE SA/NV",
    "website": "http://www.acsone.eu",
    "license": "AGPL-3",
    "category": "alc",
    "data": ["data/storage_backends.xml"],
    "installable": False,
}
