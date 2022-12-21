# -*- coding: utf-8 -*-
# Copyright 2016-2020 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2019-2020 Camptocamp
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import time
from itertools import groupby

from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Done in stock_picking_group_by_base
    # @api.model_cr
    # def init(self):
    #     # create index for the domain expressed into the
    #     # stock_move._assign_picking_group_domain method
    #     index_name = "stock_picking_groupbypartner_key_index"
    #     self.env.cr.execute(
    #         "SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,)
    #     )
    #     if not self.env.cr.fetchone():
    #         self.env.cr.execute(
    #             """
    #     CREATE INDEX %s
    #     ON %s (customer_id, partner_id, location_id, location_dest_id, picking_type_id)
    #     WHERE
    #         printed is false
    #         AND state not in ('draft', 'cancel', 'done')
    #             """,
    #             (AsIs(index_name), AsIs(self._table)),
    #         )

    # TODO: Check if still necessary
    # def _lock(self):
    #     """Lock the database rows of the picking to prevent concurrent access.

    #     The lock is released when the transaction is committed or rolled back.

    #     This method is called:
    #     1. when adding a move in the picking to prevent the picking to be started
    #     2. when detaching the picking from delivery round (no_new_picking)
    #     3. when assigning the picking to a delivery round to prevent new moves to be added
    #     """
    #     if self:
    #         _logger.info("acquire lock for pickings %s", self.ids)
    #         self.env.cr.execute(
    #             "SELECT printed FROM stock_picking WHERE id in %s FOR UPDATE",
    #             (tuple(self.ids),),
    #         )
    #         _logger.info("lock acquired for pickings %s", self.ids)
