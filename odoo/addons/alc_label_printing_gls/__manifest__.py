# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc GLS: automatically print labels",
    "description": """Alcyon: GLS automatically print labels""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "base_report_to_printer",
        "delivery_carrier_label_gls",
        "queue_job",
        # fmt: on
    ],
    "data": ["views/res_users.xml"],
    "demo": [],
    "installable": True,
}
