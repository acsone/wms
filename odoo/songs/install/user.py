# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def change_admin_language(ctx):
    """ Changing admin language """
    ctx.env.ref('base.user_root').lang = 'fr_BE'


@anthem.log
def main(ctx):
    """ Configuring products """
    change_admin_language(ctx)
