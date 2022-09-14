# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Product Animal Species",
    "description": """Product Animal Species""",
    "version": "10.0.1.0.1",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": ["product"],
    "application": False,
    "data": ["security/ir.model.access.csv", "data/animal_species.xml"],
    "demo": [],
    "external_dependencies": {"python": ["unicodecsv"]},
    'installable': False
}