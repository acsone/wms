# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import os

from odoo import models

from odoo.addons.queue_job.job import job


class ProductTemplate(models.Model):

    _inherit = "product.template"

    @job(default_channel="root.background.process")
    def _pim_import(self, vals, translations, imgs):
        """Import the data from the PIM export.
        :param vals: values to write directly
        :param translations: {lang_code: {vals}}
        :param imgs: [file_path]
        """
        self.ensure_one()
        self.write(vals)
        for lang in translations:
            self.with_context(lang=lang).write(translations[lang])
        img_start = len(self.image_ids)
        for sequence, img_path in enumerate(imgs):
            vals_img = {
                "name": os.path.basename(img_path),
                "file_type": "image",
                "alt_name": self.name,
                "data": base64.b64encode(open(img_path).read()),
            }
            img = self.env["storage.image"].create(vals_img)
            vals_rel = {
                "sequence": img_start + sequence,
                "image_id": img.id,
                "product_tmpl_id": self.id,
            }
            self.env["product.image.relation"].create(vals_rel)
