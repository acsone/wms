# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Update is_vat on account_tax")
    cr.execute("update account_tax set is_vat = True where tax_group_id=3;")
    _logger.info("%s account_tax updated", cr.rowcount)
