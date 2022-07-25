# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Delete from ir_model_data")

    cr.execute(
        """
        delete from ir_model_data where
                name = 'res_partner_category_deliver_pal' AND
                module = 'alc_stock_picking_batch_creation' AND
                model = 'res.partner.category'
    """
    )
