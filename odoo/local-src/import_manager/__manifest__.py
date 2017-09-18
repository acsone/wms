# -*- coding: utf-8 -*-
# © 2017 Okia SPRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Import Manager',
    'version': '10.0.1.0.0',
    'author': 'Okia SPRL',
    'license': 'AGPL-3',
    'category': 'Other',
    'description': """
    Manage imports from CSV file
    """,
    'depends': [
        'base',
    ],
    'data': [
        # Views
        "views/import_config_settings.xml",
        "views/import_file.xml",
    ],
    'installable': True,
}
