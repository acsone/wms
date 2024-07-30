# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Delay",
    "description": """
         Adds a maximum sale delay on customer. It is use to know if a sale
         order is taking too long to be processed by the jobs.
         """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Camptocamp SA,ACSONE SA/NV",
    "website": "https://www.camptocamp.com",
    "depends": [
        # Others
        "sale",
    ],
    "data": ["views/res_partner.xml"],
    "pre_init_hook": "pre_init_hook",
}
