# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def _set_deliveryship_csv_sending(cr, registry):
    _logger.info(
        "By default, all customers should have the flag of csv deliveryship sending to true"
    )
    cr.execute(
        """
        UPDATE
            res_partner
            SET send_csv_deliveryship = true
        WHERE
            customer = true
        """
    )


def post_init_hook(cr, registry):
    _set_deliveryship_csv_sending(cr, registry)
