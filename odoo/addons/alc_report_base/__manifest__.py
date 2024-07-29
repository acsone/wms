# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report Base",
    "summary": """
        Foundation of reporting for Alcyon""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # Custom
        "alc_company_term_condition",
        "alc_external_fax",
        "alc_queue_job_background_channel",
        # OCA
        "partner_fax",
        "queue_job",
        # fmt: on
    ],
    "assets": {
        "web.report_assets_common": [
            "alc_report_base/static/src/css/alc_report_base.css",
        ],
    },
    "data": [
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "data/paperformat.xml",
        "views/report_template.xml",
    ],
    "demo": [],
    "installable": True,
}
