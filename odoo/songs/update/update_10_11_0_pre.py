# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def delete_all_db2_importer_tables(ctx):
    """ Delete all tables for db2 importer """
    db2_importer_tables = ctx.env['db2.importer.table'].search([])
    db2_importer_tables.unlink()


@anthem.log
def delete_all_queue_jobs(ctx):
    """ Delete all queue jobs for db2 importer """
    # Because queue job can't work if db2 import tables are recreated
    queue_jobs = ctx.env['queue.job'].search([])
    queue_jobs.unlink()


@anthem.log
def main(ctx):
    """ Update 10.11.0: pre """
    delete_all_db2_importer_tables(ctx)
    delete_all_queue_jobs(ctx)
