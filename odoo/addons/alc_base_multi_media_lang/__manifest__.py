# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "AlcMedia Lang",
    "description": """
        Alcyon: Add lang on media""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "fs_base_multi_media",
        "fs_product_multi_media",
    ],  # fs_product_multi_media is required due to a bug into odoo when loading the registry
    # see https://www.odoo.com/fr_FR/my/tasks/3497266?search_in=content&search=
    "data": ["views/fs_media.xml", "views/fs_media_relation_mixin.xml"],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
