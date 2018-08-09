# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def fix_esb_backend_document_zip_name(ctx):
    """Change the document name on document zip export."""
    sql = ("UPDATE esb_backend_timestamp "
           "SET export_filename = 'Documents_{date}.zip' "
           "WHERE model='ir.attachment'")
    ctx.env.cr.execute(sql)


@anthem.log
def pre(ctx):
    """ Applying pre 10.23.0 """
    fix_esb_backend_document_zip_name(ctx)
