# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Purchase Order Ubl",
    "description": """
        Alcyon: UBL support for Purchase Order""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_purchase_order_cleaner",
        # OCA
        "purchase_order_ubl",
        "report_xml",
        # fmt: on
    ],
    "data": ["report/report_xml_purchase_order_ubl.xml"],
    "demo": [],
    "installable": True,
}
