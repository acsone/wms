# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import add_xmlid


@anthem.log
def add_xmlid_users(ctx):
    ctx.env.cr.execute("""
        SELECT res_id from ir_model_data
        WHERE model='res.users' AND module!='__setup__';
    """)
    noupdate_users_ids = ctx.env.cr.fetchall()
    users = ctx.env['res.users'].with_context(
        active_test=False).search([('id', 'not in', noupdate_users_ids)])
    for user in users:
        add_xmlid(
            ctx, user,
            '__setup__.res_user_' + user.login,
            noupdate=False
        )


def post(ctx):
    """ POST 10.28.1 """
    add_xmlid_users(ctx)
