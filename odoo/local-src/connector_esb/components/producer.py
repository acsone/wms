# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import StringIO
import zipfile

from odoo.addons.component.core import Component


class ESBZIPProducer(Component):
    _name = 'esb.zip.producer'
    _inherit = 'esb.base'
    _usage = 'zip.producer'

    def produce(self, data):
        """Generate a zip file from map records from ir.attachment"""
        zipdata = StringIO.StringIO()
        with zipfile.ZipFile(zipdata, "a", zipfile.ZIP_DEFLATED, False) as zf:
            for item in data:
                zf.writestr(
                    item['filename'] or '',
                    item['data'].decode('base64') if item['data'] else '',
                )
        zipdata.seek(0)
        return zipdata.read()
