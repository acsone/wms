# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    query = """
    UPDATE product_template AS pt
        SET no_barcode_authorized = COALESCE(
            (SELECT BOOL_AND(pp.no_barcode_authorized)
             FROM product_product AS pp
             WHERE pp.product_tmpl_id = pt.id
             GROUP BY pp.product_tmpl_id),
            FALSE -- If a template has no variants (BOOL_AND returns NULL), default to FALSE
        );
    """
    openupgrade.logged_query(cr, query)
    util.remove_field(cr, "product.product", "no_barcode_authorized")
