# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("Set the pywebdriver ip")

    cr.execute(
        """
            UPDATE
                res_users
            SET
                pywebdriver_proxy_ip = 'https://localhost:8069'
        """
    )
