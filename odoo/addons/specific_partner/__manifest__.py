# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Specific partner for Alcyon",
    "version": "10.0.2.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Sales",
    "depends": ["sale", "base_partner_sequence", "specific_base"],
    "website": "http://www.camptocamp.com",
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner.xml",
        "views/legal_entity.xml",
    ],
    "installable": False,
}
