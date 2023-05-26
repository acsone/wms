# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    _logger.info("move fields from specific_print to alc_printing_base")
    openupgrade.update_module_moved_fields(
        cr,
        "res.users",
        ["printing_pharmacy_reception_printer_id"],
        "alc_reception_pharmacy",
        "alc_reception_pharmacy_printing",
    )
