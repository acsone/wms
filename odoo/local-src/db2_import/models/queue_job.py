# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, models

CHANNEL = 'root.db2.create_or_update'
END_STATES = ['done', 'failed']


class QueueJob(models.Model):
    """Trigger inventory job when all create_or_update_record jobs are
    either done or failed.

    """
    _inherit = 'queue.job'

    @api.multi
    def write(self, vals):
        res = super(QueueJob, self).write(vals)

        for rec in self:
            if rec.channel == CHANNEL and vals.get('state') in END_STATES:
                # only do inventory if all importers are in final_update
                not_final = self.env['db2.importer'].search(
                    [('mode', '!=', 'final_update')])
                if not_final:
                    break
                count_jobs_todo = self.search_count(
                    [('state', 'not in', END_STATES),
                     ('channel', '=', CHANNEL)])
                if count_jobs_todo == 0:
                    # launch inventory
                    self.env['stock.inventory'].initial_inventory()
                    self.env['esb.backend.timestamp'].reset_timestamp()
                    self.env['ir.cron'].activate_connector()
        return res
