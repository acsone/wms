# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
{'name': 'DB2 Import',
 'summary': "Import data from DB2",
 'version': '10.0.1.0.0',
 'author': 'Camptocamp',
 'maintainer': 'Camptocamp',
 'license': 'AGPL-3',
 'category': 'Misc',
 'depends': ['sale',
             'queue_job'],
 'website': 'www.camptocamp.com',
 'data': ['views/db2_importer.xml',
          'data/db2_importer.xml'],
 'test': [],
 'installable': True,
 'auto_install': False,
 }
