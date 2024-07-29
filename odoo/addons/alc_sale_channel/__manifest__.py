# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Channel",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # fmt: off
        # OCA
        "sale_channel",
        # fmt: on
    ],
    "data": [
        "data/sale_channel.xml",
        "data/crm_lead.xml",
        "views/crm_team.xml",
        "views/sale_channel.xml",
    ],
}
