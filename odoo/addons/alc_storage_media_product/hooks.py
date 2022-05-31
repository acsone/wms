# -*- coding: utf-8 -*-
# Copyright 2021 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import SUPERUSER_ID, api


def post_init_hook(cr):
    """Loaded before installing the module.
    :param odoo.sql_db.Cursor cr:
        Database cursor.

    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref("storage_media.storage_media_backend").value = env.ref(
        "alc_storage.s3_images_backend"
    ).id
