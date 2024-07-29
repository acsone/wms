# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Pim Attribute Group",
    "description": """
        Alcyon PIM: Shared attribute's groups""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "attribute_set",
        # Others
        "product",
        # fmt: on
    ],
    "data": ["data/attribute_group.xml", "data/attribute_set.xml"],
}
