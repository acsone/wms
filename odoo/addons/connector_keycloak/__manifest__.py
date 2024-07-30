# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Connector keycloak",
    "description": """Manage Keycloak users for portal partners""",
    "version": "16.0.1.0.2",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # OCA
        "queue_job",
        "server_environment",
    ],
    "application": False,
    "data": [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "data/keycloak_backend.xml",
        "views/keycloak_backend.xml",
        "views/keycloak_user.xml",
        "wizard/keycloak_partner_wizard.xml",
        "wizard/keycloak_user_wizard.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "external_dependencies": {"python": ["python-keycloak"]},
    "pre_init_hook": "pre_init_hook",
    "installable": True,
}
