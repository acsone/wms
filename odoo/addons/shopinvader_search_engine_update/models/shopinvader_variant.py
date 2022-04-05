# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

from odoo.addons.queue_job.job import job


class ShopinvaderVariant(models.Model):

    _inherit = "shopinvader.variant"

    to_update = fields.Selection(
        selection=[("true", "True"), ("false", "False"), ("scheduled", "Scheduled")]
    )

    @job(default_channel="root.search_engine.recompute_json")
    def recompute_json(self, force_export=False):
        res = super(ShopinvaderVariant, self).recompute_json(force_export=force_export)
        self.write({"to_update": "false"})
        return res
