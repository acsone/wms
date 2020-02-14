# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'CSV File Export',
    'version': '10.0.1.0.0',
    'author': 'Okia SPRL',
    'license': 'AGPL-3',
    'category': 'Others',
    'description': """
    Module to manage CSV exports
    """,
    'depends': [
        'csv_file',
    ],
    'data': [
        "views/csv_file_export.xml",
        "wizard/csv_file_export_wizard.xml",
        "security/ir.model.access.csv",
    ],
    'website': 'http://www.camptocamp.com',
    'installable': True,
    'external_dependencies': {
        'python': ['unicodecsv'],
    },
}
