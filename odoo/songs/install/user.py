# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from pkg_resources import resource_stream
import anthem
from anthem.lyrics.loaders import load_csv_stream
from ..common import req


@anthem.log
def change_admin_language(ctx):
    """ Changing admin language """
    ctx.env.ref('base.user_root').lang = 'fr_BE'


@anthem.log
def import_users(ctx):
    """ Import users """
    content = resource_stream(req, 'data/install/res.users.csv')
    load_csv_stream(ctx, 'res.users', content, delimiter=',')


@anthem.log
def main(ctx):
    """ Configuring products """
    change_admin_language(ctx)
    import_users(ctx)
