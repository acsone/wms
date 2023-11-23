# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _migrate_14_0_2_0_0(cr):
    openupgrade.remove_tables_fks(cr, ["bank_payment_line"])


def migrate(cr, version):
    _migrate_14_0_2_0_0(cr)
