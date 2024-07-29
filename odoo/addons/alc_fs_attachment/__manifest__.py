# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Fs Storage",
    "description": """
        Filesystem storage definitions""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "fs_attachment",
        # fmt: on
    ],
    "data": [
        "data/fs_storage.xml",
    ],
    "installable": True,
}
