# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref("storage_media.storage_media_backend").value = env.ref(
        "alc_storage.s3_images_backend"
    ).id
