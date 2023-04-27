# -*- coding: utf-8 -*-
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from dateutil.relativedelta import relativedelta
from psycopg2.extensions import AsIs

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AlcDbCleaner(models.TransientModel):

    _name = "alc.db.cleaner"

    def _get_retention_period_from_config(self):
        """Get the retention period from the config parameter
        in months. (default: 24)
        """
        return self.env["ir.config_parameter"].get_param(
            "alc_db_cleaner.retention_period", 24
        )

    def _create_missing_index_if_not_exists(self):
        """Create missing index if not exists
        """
        cr = self.env.cr
        for table, column in [
            ("helpdesk_ticket", "stock_move_id"),
            ("mrp_repair_line", "move_id"),
            ("mrp_repair", "move_id"),
            ("reception_pharmacy_line", "reception_move_id"),
            ("stock_move", "main_move_id"),
            ("stock_scrap", "move_id"),
            ("helpdesk_ticket", "stock_picking_id"),
            ("stock_pack_operation_deleted", "picking_id"),
            ("stock_picking", "backorder_id"),
            ("stock_quant_package", "gls_picking_id"),
            ("stock_scrap", "picking_id"),
            ("stock_move", "procurement_id"),
            ("stock_location_route_procurement", "procurement_id"),
            ("reception_pharmacy_line", "procurement_id"),
            ("procurement_order", "mts_mto_procurement_id"),
            ("stock_pack_operation_lot", "operation_id"),
        ]:
            index_name = "{}_{}_index".format(table, column)
            cr.execute(
                """
                SELECT
                    1
                FROM
                    pg_indexes
                WHERE
                    indexname = %s
                """,
                (index_name,),
            )
            if not cr.fetchone():
                _logger.info("Create index %s on %s (%s)", index_name, table, column)
                cr.execute(
                    """
                    CREATE INDEX %s ON %s (%s) WHERE %s IS NOT NULL
                    """,
                    (AsIs(index_name), AsIs(table), AsIs(column), AsIs(column)),
                )
                # pylint: disable=invalid-commit
                cr.commit()

    def _get_max_creation_date(self):
        """Get the max creation date from the retention period
        """
        retention_period = self._get_retention_period_from_config()
        retention_date = fields.Date.to_string(
            fields.Date.from_string(fields.Date.today())
            - relativedelta(months=retention_period)
        )
        # the run is incremental. We 'all process month by month
        # starting from the oldest month to the newest month taking
        # into account the retention period
        cr = self.env.cr
        cr.execute(
            """
            SELECT
                MIN(stock_move.create_date)
            FROM
                stock_move,
                stock_location AS location_id,
                stock_location AS location_dest_id
            WHERE
                stock_move.create_date < %s
                AND state in ('done', 'cancel')
                AND location_id.id = stock_move.location_id
                AND location_dest_id.id = stock_move.location_dest_id
                AND location_id.usage in ('internal', 'transit')
                AND location_dest_id.usage in ('internal', 'transit')
            """,
            (retention_date,),
        )
        min_create_date = cr.fetchone()[0]
        if min_create_date:
            # get the first day of the next month
            new_date = fields.Date.from_string(min_create_date) + relativedelta(
                months=6
            )
            # set date at first day of the mont at  00:00:00
            new_date = new_date.replace(day=1)
            retention_date = fields.Date.to_string(new_date)
            return retention_date
        return None

    def _prune_stock_moves(self, max_creation_date):
        """Prune stock move created before the max creation date and
        location_id and location_dest_id.usage is in ('internal', 'transit'))
        """
        _logger.info("Start pruning stock move...")
        cr = self.env.cr
        # Create a temporary table to store the ids of the stock move to delete
        cr.execute(
            """
            DROP TABLE IF EXISTS stock_move_to_delete;
            CREATE TEMPORARY TABLE
                stock_move_to_delete
            AS
                SELECT
                    stock_move.id
                FROM
                    stock_move,
                    stock_location AS location_id,
                    stock_location AS location_dest_id
                WHERE
                    stock_move.create_date < %s
                    AND state in ('done', 'cancel')
                    AND location_id.id = stock_move.location_id
                    AND location_dest_id.id = stock_move.location_dest_id
                    AND location_id.usage in ('internal', 'transit')
                    AND location_dest_id.usage in ('internal', 'transit')
        """,
            (max_creation_date,),
        )

        # Remove chained moves
        _logger.info("Removing chained moves")
        cr.execute(
            """
            UPDATE
                stock_move
            SET
                move_dest_id = NULL
            WHERE
                move_dest_id IN (SELECT id FROM stock_move_to_delete)
        """
        )
        _logger.info(
            "stock.move: %s records modified to remove chained moves", cr.rowcount
        )
        # Remove stock pack operations lot
        _logger.info("Removing stock pack operations lot")
        cr.execute(
            """
            DELETE FROM
                stock_pack_operation_lot
            USING
                stock_move_operation_link,
                stock_move_to_delete
            WHERE
                stock_pack_operation_lot.operation_id = stock_move_operation_link.operation_id
                AND stock_move_operation_link.move_id = stock_move_to_delete.id
        """
        )
        _logger.info("stock.pack.operation.lot: %s records deleted", cr.rowcount)

        # Remove stock pack operations
        _logger.info("Removing stock pack operations")
        cr.execute(
            """
            DELETE FROM
                stock_pack_operation
            USING
                stock_move_operation_link,
                stock_move_to_delete
            WHERE
                stock_pack_operation.id = stock_move_operation_link.operation_id
                AND stock_move_operation_link.move_id = stock_move_to_delete.id
        """
        )
        _logger.info("stock.pack.operation: %s records deleted", cr.rowcount)

        # remove stock moves
        _logger.info("Removing stock move")
        cr.execute(
            """
            DELETE FROM
                stock_move
            USING
                stock_move_to_delete
            WHERE
                stock_move.id = stock_move_to_delete.id
        """
        )
        _logger.info("stock.move: %s records deleted", cr.rowcount)

        # remove orphan pack operations
        _logger.info("Removing orphan stock pack operations")
        cr.execute(
            """
            DELETE FROM
                stock_pack_operation
            WHERE
                NOT EXISTS (
                    SELECT
                        1
                    FROM
                        stock_move_operation_link
                    WHERE
                        operation_id = stock_pack_operation.id
                );
        """
        )
        _logger.info("stock.pack.operation: %s records deleted", cr.rowcount)

        # remove orphan pack operations lot
        _logger.info("Removing orphan stock pack operations lot")
        cr.execute(
            """
            DELETE FROM
                stock_pack_operation_lot
            WHERE
                NOT EXISTS (
                    SELECT
                        1
                    FROM
                        stock_pack_operation
                    WHERE
                        stock_pack_operation.id = stock_pack_operation_lot.operation_id
                );
        """
        )
        _logger.info("stock.pack.operation.lot: %s records deleted", cr.rowcount)

    def _prune_stock_pickings(self, max_creation_date):
        """Prune stock pickings created before the max creation date and
        no more linked to a stock move
        """
        _logger.info("Start pruning stock pickings")
        cr = self.env.cr
        # Create a temporary table to store the ids of the stock picking to delete
        cr.execute(
            """
            DROP TABLE IF EXISTS stock_picking_to_delete;
            CREATE TEMPORARY TABLE
                stock_picking_to_delete
            AS
                SELECT
                    id
                FROM
                    stock_picking
                WHERE
                    not exists (
                        SELECT 1 FROM stock_move
                        WHERE stock_move.picking_id = stock_picking.id
                    )
                    AND stock_picking.create_date < %s
                    AND state in ('done', 'cancel')
        """,
            (max_creation_date,),
        )

        # Remove item from mail_message
        _logger.info("Removing mail messages related to stock pickings")
        cr.execute(
            """
            DELETE FROM
                mail_message
            USING
                stock_picking_to_delete
            WHERE
                stock_picking_to_delete.id = mail_message.res_id
                AND mail_message.model = 'stock.picking'
        """
        )
        _logger.info("mail.message: %s records deleted", cr.rowcount)

        # Remove item from mail_followers
        _logger.info("Removing mail followers related to stock pickings")
        cr.execute(
            """
            DELETE FROM
                mail_followers
            USING
                stock_picking_to_delete
            WHERE
                stock_picking_to_delete.id = mail_followers.res_id
                AND mail_followers.res_model = 'stock.picking'
        """
        )
        _logger.info("mail.followers: %s records deleted", cr.rowcount)

        # Remove orphans pack operations
        _logger.info("Removing orphans pack operations related to stock pickings")
        cr.execute(
            """
            DELETE FROM
                stock_pack_operation
            USING
                stock_picking_to_delete
            WHERE
                stock_picking_to_delete.id = stock_pack_operation.picking_id
                """
        )
        _logger.info("stock.pack.operation: %s records deleted", cr.rowcount)

        # Remove history of deleted pack operations
        _logger.info("Removing history of deleted pack operations")
        cr.execute(
            """
            DELETE FROM
                stock_pack_operation_deleted
            USING
                stock_picking_to_delete
            WHERE
                stock_picking_to_delete.id = stock_pack_operation_deleted.picking_id
        """
        )
        _logger.info("stock.pack.operation.deleted: %s records deleted", cr.rowcount)

        # Un reference backorder_id
        _logger.info("Un referencing backorder_id")
        cr.execute(
            """
            UPDATE
                stock_picking
            SET
                backorder_id = NULL
            FROM
                stock_picking_to_delete
            WHERE
                stock_picking_to_delete.id = stock_picking.backorder_id
        """
        )
        _logger.info(
            "stock.picking: %s records modified to remove backorder_id", cr.rowcount
        )

        # Remove item from stock_picking
        _logger.info("Removing stock pickings")
        cr.execute(
            """
            DELETE FROM
                stock_picking
            USING
                stock_picking_to_delete
            WHERE
                stock_picking.id = stock_picking_to_delete.id
        """
        )
        _logger.info("stock.picking: %s records deleted", cr.rowcount)

    def _prune_procurement_orders(self, max_creation_date):
        """Prune procurement order created before the max creation date and
        done or cancel
        """
        _logger.info("Start pruning procurement order")
        cr = self.env.cr
        # Create a temporary table to store the ids of the procurement order to delete
        cr.execute(
            """
            DROP TABLE IF EXISTS procurement_order_to_delete;
            CREATE TEMPORARY TABLE
                procurement_order_to_delete
            AS
                SELECT
                    id
                FROM
                    procurement_order
                WHERE
                    create_date < %s
                    AND state in ('done', 'cancel')
        """,
            (max_creation_date,),
        )

        # Remove item from mail_message
        _logger.info("Removing mail messages related to procurement orders")
        cr.execute(
            """
            DELETE FROM
                mail_message
            USING
                procurement_order_to_delete
            WHERE
                procurement_order_to_delete.id = mail_message.res_id
                AND mail_message.model = 'procurement.order'
        """
        )
        _logger.info("mail.message: %s records deleted", cr.rowcount)

        # Remove item from mail_followers
        _logger.info("Removing mail followers related to procurement orders")
        cr.execute(
            """
            DELETE FROM
                mail_followers
            USING
                procurement_order_to_delete
            WHERE
                procurement_order_to_delete.id = mail_followers.res_id
                AND mail_followers.res_model = 'procurement.order'
        """
        )
        _logger.info("mail.followers: %s records deleted", cr.rowcount)

        # Remove item from procurement_order
        _logger.info("Removing procurement orders")
        cr.execute(
            """
            DELETE FROM
                procurement_order
            USING
                procurement_order_to_delete
            WHERE
                procurement_order.id = procurement_order_to_delete.id
        """
        )
        _logger.info("procurement.order: %s records deleted", cr.rowcount)

    def _prune_mail_messages(self, max_creation_date):
        """Prune mail some messages created before the max creation date
        """
        _logger.info("Start pruning mail messages")
        cr = self.env.cr
        # delete mail_message for queue_job older than 1 month
        _logger.info("Removing mail messages related to queue jobs")
        cr.execute(
            """
            DELETE FROM
                mail_message
            WHERE
                model = 'queue.job'
                AND create_date < now() - interval '1 month'
        """
        )
        _logger.info("mail.message: %s records deleted for queue.job", cr.rowcount)

        # delete mail_followers for queue_job older than 1 month
        _logger.info("Removing mail followers related to queue jobs")
        cr.execute(
            """
            DELETE FROM
                mail_followers
            WHERE
                res_model = 'queue.job'
        """
        )
        _logger.info("mail.followers: %s records deleted for queue.job", cr.rowcount)

        # delete mail_message with body like 'created' or 'créé' max_creation_date
        _logger.info(u"Removing mail messages with body like 'created' or 'créé'")
        cr.execute(
            """
            DELETE FROM
                mail_message
            WHERE
                body like '%%created%%'
                OR body like '%%créé%%'
                AND create_date < %s
        """,
            (max_creation_date,),
        )
        _logger.info("mail.message: %s records deleted for created", cr.rowcount)

    def _prune_zetes_logger(self):
        _logger.info("Start pruning zetes logger")
        cr = self.env.cr
        cr.execute(
            """
            DELETE FROM
                zetes_logger
            """
        )
        _logger.info("zetes_logger: %s records deleted", cr.rowcount)

    @api.multi
    def doit(self):
        max_creation_date = self._get_max_creation_date()
        self._create_missing_index_if_not_exists()
        self._prune_zetes_logger()
        if max_creation_date:
            _logger.info(
                "\n"
                "----------------------------------------------\n"
                "Start pruning for max creation date %s\n"
                "----------------------------------------------",
                max_creation_date,
            )
            self._prune_stock_moves(max_creation_date)
            self._prune_stock_pickings(max_creation_date)
            self._prune_procurement_orders(max_creation_date)
            self._prune_mail_messages(max_creation_date)
        return True

    @api.model
    def _cron_do_cleanup(self):
        return self.new({}).doit()
