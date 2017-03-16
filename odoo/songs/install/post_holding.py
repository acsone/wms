# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def cleanup(ctx):
    """ Remove dummy account on main company """
    ctx.env.ref('__setup__.dummy_holding_account').unlink()
