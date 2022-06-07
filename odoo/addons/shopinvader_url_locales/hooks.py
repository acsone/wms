# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def post_init_hook(cr, registry):
    if not column_exists(cr, "shopinvader_variant", "to_update"):
        return
    _logger.info("Mark product re export")
    cr.execute(
        """
        UPDATE
            shopinvader_variant
        SET
            to_update = 'true'
        WHERE
            active
    """
    )
    _logger.info("%s variants to re export", cr.rowcount)

    _logger.info("Schedule export of shopinvader category")
    env = api.Environment(cr, SUPERUSER_ID, {})
    category_model = env.ref("shopinvader.model_shopinvader_category")
    env["se.index"].search(
        [("model_id", "=", category_model.id)]
    ).recompute_all_binding(force_export=True)
