# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from datetime import datetime, timedelta

from odoo import fields


@anthem.log
def enable_pharmacy_export(ctx):
    """Enable cron for pharmacy export at 01:00"""
    tomorrow = datetime.today() + timedelta(days=1)
    next_call = tomorrow.replace(hour=1, minute=0, second=0)
    cronjob = ctx.env.ref('connector_esb.ir_cron_esb_export_pharmacy')
    cronjob.write({
        'active': True,
        'nextcall': fields.Datetime.to_string(next_call),
    })


@anthem.log
def enable_promotion_alcyon_export(ctx):
    """Enable cron for promotion alcyon export at 01:30"""
    tomorrow = datetime.today() + timedelta(days=1)
    next_call = tomorrow.replace(hour=1, minute=30, second=0)
    cronjob = ctx.env.ref('connector_esb.ir_cron_esb_export_promotion_alcyon')
    cronjob.write({
        'active': True,
        'nextcall': fields.Datetime.to_string(next_call),
    })


@anthem.log
def main(ctx):
    """Activate cron jobs for ESB connector."""
    enable_pharmacy_export(ctx)
    enable_promotion_alcyon_export(ctx)
