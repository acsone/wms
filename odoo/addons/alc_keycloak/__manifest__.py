# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    "name": "Alcyon Keycloak",
    "description": """Alcyon Keycloak""",
    "version": "10.0.1.0.4",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        "keycloak",
        "alc_elasticsearch_security",
        "alc_eshop_ordering_allowed",
        "alc_veterinary_group",
        "specific_sale",  # for help_with_fee to be moved in a dedicated addon
    ],
    "application": False,
    "data": [],
    "demo": [],
    'installable': False
}