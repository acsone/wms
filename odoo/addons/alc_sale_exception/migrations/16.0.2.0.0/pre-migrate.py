# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from openupgradelib import openupgrade

from odoo.tools import sql

_logger = logging.getLogger(__name__)


def _init_main_exception_id(env):
    """Initialize main_exception_id field for existing records.

    Add the column if not exists and set the value to the first exception_id
    """
    if not sql.column_exists(env.cr, "sale_order_line", "main_exception_id"):
        _logger.info("Add main_exception_id column to sale_order_line")
        # add the column
        query = """
            ALTER TABLE sale_order_line
            ADD COLUMN main_exception_id integer
        """
        env.cr.execute(query)
        # add the FK constraint to exception_rule
        query = """
            ALTER TABLE sale_order_line
            ADD CONSTRAINT sale_order_line_main_exception_id_fkey
            FOREIGN KEY (main_exception_id)
            REFERENCES exception_rule(id)
            ON DELETE SET NULL
        """
        env.cr.execute(query)
        # set the value
        # we take the id of the rule with the lower sequence  linked to the line
        # through the exception_rule_sale_order_line_rel table
        # we create a CTE with the first rule id for each line
        query = """
            WITH all_exceptions AS (
                SELECT
                    e.sale_order_line_id,
                    e.exception_rule_id,
                    ROW_NUMBER() OVER (PARTITION BY e.sale_order_line_id ORDER BY er.sequence) AS rn
                FROM
                    exception_rule_sale_order_line_rel e
                    INNER JOIN exception_rule er ON e.exception_rule_id = er.id
            ),
            main_exception AS (
                SELECT sale_order_line_id, exception_rule_id
                FROM all_exceptions
                WHERE rn = 1
            )
            UPDATE
                sale_order_line
            SET
                main_exception_id = exception_rule_id
            FROM
                main_exception
            WHERE
                sale_order_line.id = main_exception.sale_order_line_id
                """
        env.cr.execute(query)
        _logger.info(
            "main_exception_id field initialized for existing %d records",
            env.cr.rowcount,
        )


@openupgrade.migrate()
def migrate(env, version):
    _init_main_exception_id(env)
