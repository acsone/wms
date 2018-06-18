# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.modules import update_translations


@anthem.log
def update_esb_backend_data(ctx):
    """Changing erroneous filename of esb product export
    """
    sql = ("UPDATE esb_backend_timestamp "
           "SET export_filename = 'Products_{date}.xml' where kind='product'")
    ctx.env.cr.execute(sql)


@anthem.log
def post(ctx):
    """ Applying post 10.21.1 """
    update_translations(ctx, ['specific_sale',
                              'specific_followup'])
    update_esb_backend_data(ctx)
