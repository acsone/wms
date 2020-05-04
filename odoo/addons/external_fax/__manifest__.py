# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "External fax",
    "description": "Send fax using an external service",
    "version": "10.0.1.0.0",
    "author": "Camptocamp",
    "license": "AGPL-3",
    "category": "Communication",
    "depends": ["mail", "queue_job"],
    "website": "http://www.camptocamp.com",
    "data": ["data/fax.external.csv", "security/ir.model.access.csv"],
    "installable": True,
}
