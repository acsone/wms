# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Uninstall account_cutoff_accrual_sale_stock_sale_invoice_policy")
    query = """
        UPDATE ir_module_module
            SET state = 'to remove'
            WHERE name = 'account_cutoff_accrual_sale_stock_sale_invoice_policy';
    """
    openupgrade.logged_query(cr, query)
