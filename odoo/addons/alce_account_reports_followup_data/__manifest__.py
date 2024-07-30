{
    "name": "Alc account followup for Alcyon",
    "version": "16.0.1.0.0",
    "author": "ACSONE SA/NV",
    "license": "Other proprietary",
    "category": "Others",
    "description": """
    Specific account followup date for Alcyon
    """,
    # BE CAREFUL ALL the dependencies must BE LGPL or OEEL!!!
    # account_reports_followup is an Odoo enterprise module
    "depends": [
        # Others
        "account_followup",
        "snailmail_account_followup",
    ],
    "data": ["data/followup_line.xml"],
    "installable": True,
    "pre_init_hook": "pre_init_hook",
}
