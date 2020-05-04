# -*- coding: utf-8 -*-
# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Invoice Sent",
    "version": "1.0",
    "author": "BCIM",
    "license": "AGPL-3",
    "category": "Accounting & Finance",
    "depends": ["account", "web_notify", "queue_job"],
    "data": [
        "views/account_invoice.xml",
        "views/account_invoice_print_views.xml",
        "views/res_partner.xml",
        "security/ir.model.access.csv",
        "wizards/account_invoice_state_view.xml",
    ],
    "installable": True,
}
