# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL

{
    "name": "Split CODA",
    "version": "10.0.1.0.0",
    "author": "Okia",
    "maintainer": "QANSEE",
    "category": "Accounting",
    "website": "http://www.okia.be",
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # l10n_be_coda is an Odoo enterprise module
    "depends": ["l10n_be_coda"],
    "data": [],
    "installable": True,
    "auto_install": False,
    "license": "Other proprietary",
    "application": False,
    "pre_init_hook": "pre_init_hook",
}
