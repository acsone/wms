# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def update_esb_backend_timestamp(ctx):
    """Changing empty timestamp kind for documents."""
    sql = ("UPDATE esb_backend_timestamp "
           "SET kind = 'documents' where model='ir.attachment'")
    ctx.env.cr.execute(sql)


@anthem.log
def post(ctx):
    """ Applying pre 10.22.0 """
    update_esb_backend_timestamp(ctx)
