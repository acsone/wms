# -*- coding: utf-8 -*-
{
    "name": "Specific account followup for Alcyon",
    "version": "10.0.1.0.0",
    "author": "Sylvain Van Hoof",
    "license": "Other proprietary",
    "category": "Others",
    "description": """
    Specific account followup for Alcyon
    """,
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # account_reports_followup is an Odoo enterprise module
    "depends": ["account_reports_followup"],
    "data": ["data/followup_line.xml"],
    "website": "http://www.camptocamp.com",
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
