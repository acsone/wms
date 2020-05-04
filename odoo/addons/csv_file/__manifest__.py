# -*- coding: utf-8 -*-
# Copyright 2018 Okia SPRL <Sylvain Van Hoof>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "FTP Connector",
    "version": "10.0.1.0.0",
    "author": "Okia SPRL",
    "license": "AGPL-3",
    "category": "Others",
    "description": """
    FTP Manager
    """,
    "depends": ["base"],
    "data": [
        "views/ftp_connector.xml",
        "views/csv_file_logger.xml",
        "security/ir.model.access.csv",
    ],
    "website": "http://www.camptocamp.com",
    "installable": True,
    "external_dependencies": {"python": ["paramiko"]},
}
