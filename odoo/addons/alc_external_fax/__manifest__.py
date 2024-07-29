# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "External fax",
    "description": "Send fax using an external service",
    "version": "16.0.1.0.0",
    "author": "Camptocamp,ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Communication",
    "depends": [
        # fmt: off
        # OCA
        "queue_job",
        # Others
        "mail",
        # fmt: on
    ],
    "website": "https://acsone.eu",
    "data": [
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "data/fax.external.csv",
        "security/ir.model.access.csv",
    ],
    "pre_init_hook": "pre_init_hook",
}
