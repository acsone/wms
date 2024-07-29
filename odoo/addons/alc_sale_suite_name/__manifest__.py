# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Suite Name",
    "summary": """
        Alcyon: Manage suite name on sale orders""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Others
        "sale",
        # fmt: on
    ],
    "data": ["views/res_partner.xml", "views/sale_order.xml"],
    "installable": True,
}
