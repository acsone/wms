# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from odoo.addons.queue_job.job import job


class ProductTemplate(models.Model):

    _inherit = "product.template"

    @job(default_channel="root.background.process")
    def shopinvader_manual_export(self):
        self.mapped("product_variant_ids").shopinvader_manual_export()
