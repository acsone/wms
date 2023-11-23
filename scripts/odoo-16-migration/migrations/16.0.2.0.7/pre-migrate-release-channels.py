# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _create_shipment_advice_column(cr):
    """Pre create the column before populating it in the post command."""
    query = """
        ALTER TABLE stock_picking
        ADD COLUMN planned_shipment_advice_id INTEGER
    """
    openupgrade.logged_query(cr, query)


def migrate(cr, version):
    _create_shipment_advice_column(cr)
