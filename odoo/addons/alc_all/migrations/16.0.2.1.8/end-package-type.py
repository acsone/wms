# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _remove_pack_type(env):
    """Remove unused package types."""

    query = """
         stock_package_type
            WHERE name NOT LIKE 'A%'
            AND name NOT LIKE 'E%'
            AND name NOT LIKE 'GLS%'
            AND name NOT LIKE 'I%'
            AND name NOT LIKE 'N%'
            AND name NOT LIKE 'Q%'
    """
    openupgrade.logged_query(env.cr, query)


def _create_package_type_box(env):
    """Create package types 'Box'."""
    # Create temporary field
    query = """
        ALTER TABLE stock_package_type ADD COLUMN is_a_box BOOLEAN;
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        INSERT INTO stock_package_type (create_date, name, number_of_parcels, package_carrier_type, is_a_box)
            SELECT NOW() at time zone 'UTC', 'Boîte ' || i::text, i, 'none', True
                FROM generate_series(1, 10) as t(i)
    """
    openupgrade.logged_query(env.cr, query)


def _upgrade_quant_packages_box(env):
    """
    Upgrade quant pacakges to set the box corresponding to.

    the former field nbr_packages for locations:

        - Output
        - Customers
        - Consignemnts (direct children)
    """
    query = """
        UPDATE stock_quant_package sqp
            SET package_type_id = (SELECT id FROM stock_package_type WHERE number_of_parcels = sqp.nbr_packages AND is_a_box = True), number_of_parcels = (SELECT number_of_parcels FROM stock_package_type WHERE number_of_parcels = sqp.nbr_packages AND is_a_box = True)
            WHERE (location_id IN (SELECT sl.id FROM stock_location sl JOIN stock_warehouse sw ON sw.wh_output_stock_loc_id = sl.id)
            OR location_id IN (SELECT id FROM stock_location where usage = 'customer')
            OR location_id IN (select sl.id FROM stock_location sl JOIN stock_location sl_p ON sl.location_id = sl_p.id WHERE sl_p.name = 'Consignment' AND sl_p.usage = 'view'))
            AND (package_type_id IS NULL OR package_type_id NOT IN (19164, 22117))
    """
    openupgrade.logged_query(env.cr, query)

    query = """
        ALTER TABLE stock_package_type DROP COLUMN is_a_box;
    """
    openupgrade.logged_query(env.cr, query)


@openupgrade.migrate()
def migrate(env, version):
    _remove_pack_type(env)
    _create_package_type_box(env)
    _upgrade_quant_packages_box(env)
