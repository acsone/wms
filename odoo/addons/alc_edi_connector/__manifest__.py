# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Edi Connector",
    "description": """
        Alcyon EDI connector""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Custom
        "alc_purchase_order_ubl",
        # OCA
        "connector",
        "purchase_order_approved",
        "purchase_order_ubl",
        "queue_job",
        "queue_job_cron",
        # Others
        "stock",
    ],
    "data": [
        "security/edi_backend.xml",
        "security/edi_export_task_def.xml",
        "security/edi_import_task_def.xml",
        "security/res_groups.xml",
        "views/res_partner.xml",
        "views/edi_backend.xml",
        "views/purchase_order.xml",
        "data/ir_cron.xml",
        "data/queue_job.xml",
    ],
    "demo": ["demo/alc_edi_connector.xml"],
    "external_dependencies": {"python": ["paramiko", "slugify"]},
    "installable": True,
}
