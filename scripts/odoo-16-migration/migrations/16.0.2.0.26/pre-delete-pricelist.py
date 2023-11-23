# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _delete_old_pricelist(cr):
    # This pricelist seems to have been deleted and relational keys not
    query = """
        DELETE FROM partner_discount_pricelist_rel WHERE pricelist_id = 77
    """
    openupgrade.logged_query(cr, query)

    query = """
        DELETE FROM order_discount_pricelist_rel WHERE pricelist_id = 77
    """
    openupgrade.logged_query(cr, query)


def migrate(cr, version):
    _delete_old_pricelist(cr)
