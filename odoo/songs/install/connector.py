# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def activate_connector(ctx):
    """Activate cron jobs and set some timestamp for ESB connector."""
    # This song is used for testing the job that is called on initialisation
    ctx.env['esb.backend.timestamp'].reset_timestamp()
    ctx.env['ir.cron'].activate_connector()


@anthem.log
def main(ctx):
    activate_connector(ctx)
