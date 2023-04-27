# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from openupgradelib import openupgrade

from odoo.tools import sql

_logger = logging.getLogger(__name__)
XML_IDS = ["no_line_under_0", "no_line_at_zero", "order_amount_minimum"]


def pre_init_hook(cr):
    _logger.info("move xml_ids from sale_specific to alc_sale_exception")
    openupgrade.rename_xmlids(
        cr,
        [
            (f"specific_sale.{xml_id}", f"alc_sale_exception.{xml_id}")
            for xml_id in XML_IDS
        ],
    )


def post_init_hook(cr, registry):
    _logger.info("set is_blocking to true on rules that are not warning_only")
    if sql.column_exists(cr, "exception_rule", "warning_only"):
        query = """UPDATE exception_rule
                   SET is_blocking = True
                   WHERE warning_only != TRUE or warning_only is NULL"""
        cr.execute(query)
