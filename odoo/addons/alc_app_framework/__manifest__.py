# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Framework App",
    "description": """
        Gather all framework related modules for Alcyon""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "application": True,
    "depends": [
        # fmt: off
        # Custom
        "alc_base_auto_join",
        "alc_cerberus_utils",
        "alc_queue_job_security",
        # OCA
        "base_import_security_group",
        "base_optional_quick_create",
        "mail_environment",
        "queue_job_cron",
        "report_csv",
        "rest_log",
        "server_action_mass_edit",
        # fmt: on
    ],
}
