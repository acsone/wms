# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Partner Sequence",
    "description": """
        Prevents the propagation of a parent ref to its children, for instance from a
        vet practice to a specific vet in that practice""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # fmt: off
        # OCA
        "base_partner_sequence",
        # fmt: on
    ],
    "data": ["views/res_partner.xml"],
    "demo": [],
}
