# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alcyon Documents",
    "description": """Alcyon Documents""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_b2c_partner",
        "alc_partner_type",
        "alc_queue_job_background_channel",
        # OCA
        "queue_job",
        "sale_channel",
        # Others
        "sale",
        "stock",
    ],
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/alc_document.xml",
        "views/res_partner.xml",
        "data/queue_job_function.xml",
    ],
    "demo": [],
    "installable": True,
}
