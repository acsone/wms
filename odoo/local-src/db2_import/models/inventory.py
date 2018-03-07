# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import api, models
from odoo.addons.queue_job.job import job


INVENTORY_REFS = [
    '__setup__.initial_inventory',
    '__setup__.initial_inventory_no_lot',
]


class Inventory(models.Model):
    _inherit = 'stock.inventory'

    @api.model
    def initial_inventory(self):
        for ref in INVENTORY_REFS:
            inventory = self.env.ref(ref, raise_if_not_found=False)
            if inventory:
                # create one job per inventory
                inventory.with_delay().job_initial_inventory()

    @api.multi
    @job(default_channel='root.inventory_init')
    def job_initial_inventory(self):
        self.prepare_inventory()
        self.action_done()
