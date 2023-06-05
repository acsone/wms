# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import string

from openupgradelib import openupgrade


def _deactivate_constraint(env):
    query = """
        UPDATE ir_config_parameter
            SET value = False
            WHERE key = 'alc_stock_location_constraint.stock_location_constraint'
    """
    openupgrade.logged_query(env.cr, query)


def _activate_constraint(env):
    query = """
        UPDATE ir_config_parameter
            SET value = True
            WHERE key = 'alc_stock_location_constraint.stock_location_constraint'
    """
    openupgrade.logged_query(env.cr, query)


def _change_columns(env):
    if openupgrade.column_exists(env.cr, "stock_location", "shelf"):
        # Moving shelf data to rack one
        query = """
            UPDATE stock_location
                SET rack = shelf
                WHERE rack IS NULL AND shelf IS NOT NULL
        """
        openupgrade.logged_query(env.cr, query)

    if openupgrade.column_exists(env.cr, "stock_location", "height"):
        # Moving height data to level one
        query = """
            UPDATE stock_location
                SET level = height
                WHERE level IS NULL AND height IS NOT NULL
        """
        openupgrade.logged_query(env.cr, query)


def _compute_zone(env):
    """Set the property 'is_zone' on proper locations from v10 data."""
    query = """
        SELECT id
            FROM stock_location
            WHERE id IN
                (SELECT distinct(location_id)
                    FROM stock_location sl
                    WHERE picking_zone_id IS NOT NULL
                    AND EXISTS(
                        SELECT 1
                            FROM stock_location
                            WHERE id = sl.location_id
                            AND usage = 'view'
                            AND picking_zone_id IS NOT NULL));

    """
    openupgrade.logged_query(env.cr, query)
    results = env.cr.fetchall()
    ids = [r[0] for r in results]
    zone_locations = env["stock.location"].browse(ids)
    zone_locations.write({"is_zone": True})
    zone_locations.flush_recordset()


def _update_box(env):
    """
    To update the box value which can be a number or a string,.

    we use the letter number if the box is a string (e.g.: a=1, b=2, ...)

    We have only those location box cases:
        - 1 (integer)
        - 2A (string)

    Impossible easily to do it in a single query, so we rely both on
    sql and orm.
    """

    if openupgrade.column_exists(env.cr, "stock_location", "box"):
        dict_ord = {}
        for letter in list(string.ascii_lowercase):
            dict_ord[letter] = ord(letter) - 96

        # We first do a query to get the box value as it is not in registry anymore
        query = """
            SELECT id, box
                FROM stock_location WHERE box IS NOT NULL;
        """
        env.cr.execute(query)
        results = env.cr.fetchall()

        for result in results:
            location = env["stock.location"].browse(result[0])
            if str.isnumeric(result[1]):
                # If entire box is a numeric (eg.: 01 or 12)
                location.posx = int(result[1])
            else:
                # Take the first character
                if str.isnumeric(result[1][0]):
                    location.posx = int(result[1][0])
                else:
                    if result[1][0].lower() in dict_ord:
                        location.posx = dict_ord[result[1][0].lower()]
                if len(result[1]) > 1:
                    if str.isnumeric(result[1][1]):
                        location.posx = int((location.posx * 10) + int(result[1][1]))
                    else:
                        if result[1][1].lower() in dict_ord:
                            location.posx = int(
                                (location.posx * 10) + dict_ord[result[1][1].lower()]
                            )


@openupgrade.migrate()
def migrate(env, version):
    _deactivate_constraint(env)
    _compute_zone(env)
    _change_columns(env)
    _update_box(env)
    _activate_constraint(env)
