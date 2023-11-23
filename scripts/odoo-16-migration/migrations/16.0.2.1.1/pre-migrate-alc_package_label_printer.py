# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def _mig_res_users(cr):
    if not openupgrade.column_exists(
        cr, "res_users", "printing_package_label_printer_id"
    ):
        return
    cr.execute(
        """
        ALTER TABLE res_users
        ADD COLUMN IF NOT EXISTS default_label_printer_id integer;
        UPDATE res_users
        SET default_label_printer_id=printing_package_label_printer_id;
        """
    )


def migrate(cr, version):
    _mig_res_users(cr)
