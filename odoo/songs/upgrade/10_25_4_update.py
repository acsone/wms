# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def set_cron_to_noupdate(ctx):
    """Set pesky cron to noupdate"""
    sql = ("UPDATE ir_model_data"
           "    SET noupdate = true"
           "    WHERE name = 'generate_procurement_order' AND"
           "          module = 'specific_purchase' AND"
           "          model='ir.cron'")
    ctx.env.cr.execute(sql)


def set_db2_importer_priorities(ctx):
    """Set value in `priority` field on noupdate xml records"""
    ref = ctx.env.ref
    ref('db2_import.db2_purchase_importer').priority = 10
    ref('db2_import.db2_sale_importer').priority = 10
    ref('db2_import.db2_ticket_importer').priority = 11


anthem.log
def post(ctx):
    """ POST 10.25.4 """
    set_cron_to_noupdate(ctx)
    set_db2_importer_priorities(ctx)
