# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)

{
    "name": "Specific purchase report for Alcyon",
    "version": "10.0.1.0.1",
    "author": "Camptocamp",
    "license": "Other proprietary",
    "category": "Report",
    "depends": ["alc_oeel_helpdesk", "purchase"],
    "website": "http://www.camptocamp.com",
    "data": [],
    "installable": True,
    "external_dependencies": {"python": ["openupgradelib"]},
    "pre_init_hook": "pre_init_hook",
}
