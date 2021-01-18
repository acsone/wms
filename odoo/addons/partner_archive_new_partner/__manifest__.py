# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Archive Select New Partner",
    "summary": "Select a new partner upon archiving",
    "version": "10.0.1.0.0",
    "category": "Partner",
    "website": "https://github.com/OCA/partner-contact",
    "author": "Camptocamp SA," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["sale", "stock", "account"],
    "data": ["wizards/partner_archive_views.xml", "views/res_partner.xml"],
}
