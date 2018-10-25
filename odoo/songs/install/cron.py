# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def deactivate_all(ctx):
    """Deactivate all cron jobs.

    In first go live step when recovering datas
    the database must be mostly inactive.

    """
    crons = ctx.env['ir.cron'].search([])
    if crons:
        crons.write({'active': False})
