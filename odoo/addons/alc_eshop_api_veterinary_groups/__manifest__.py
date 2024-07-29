# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Eshop Veterinary Group",
    "description": """
        Alcyon: Expose veterinary_group info to eshop""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_veterinary_group",
        # OCA
        "fastapi",
        # fmt: on
    ],
    "data": [],
    "demo": [],
    "installable": True,
}
