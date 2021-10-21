# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import hashlib
import logging
import struct

from odoo.osv import expression

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    _advisory_lock_name = "shopfloor_batch_picking_create"

    def _select_a_picking_batch(self, batches):
        batch = super(ClusterPicking, self)._select_a_picking_batch(batches)
        if not batch and self.work.menu.batch_create:
            batch = self._batch_auto_create()
            batch.write({"user_id": self.shopfloor_user.id, "state": "in_progress"})
        return batch

    def _batch_picking_base_search_domain(self):
        domain = super(ClusterPicking, self)._batch_picking_base_search_domain()
        return expression.AND(
            [
                domain,
                [
                    (
                        "picking_ids.picking_type_id",
                        "in",
                        self.work.menu.picking_type_ids.ids,
                    )
                ],
            ]
        )

    def _batch_auto_create(self):
        self._lock()
        menu = self.work.menu
        wizard = self.env["make.picking.batch"].create(
            {
                "picking_type_ids": [(6, None, menu.picking_type_ids.ids)],
                "stock_device_type_ids": [(6, None, menu.stock_device_type_ids.ids)],
                "maximum_number_of_preparation_lines": menu.maximum_number_of_preparation_lines,
                "user_id": self.shopfloor_user.id,
            }
        )
        return wizard._create_batch(raise_if_not_possible=False)

    def _lock(self):
        """Lock to prevent concurrent creation of batch
        Use a blocking advisory lock to prevent 2 transactions to create
        a batch at the same time. The lock is released at the commit or
        rollback of the transaction.
        The creation of a new batch should be short enough not to block
        the users for too long.
        """
        _logger.info(
            "trying to acquire lock to create a picking batch (%s)", self.env.user.login
        )
        hasher = hashlib.sha1(str(self._advisory_lock_name).encode())
        # pg_lock accepts an int8 so we build an hash composed with
        # contextual information and we throw away some bits
        int_lock = struct.unpack("q", hasher.digest()[:8])

        self.env.cr.execute("SELECT pg_advisory_xact_lock(%s);", (int_lock,))
        self.env.cr.fetchone()[0]  # pylint: disable=expression-not-assigned
        # Note: if the lock had to wait, the snapshot of the transaction is
        # very much probably outdated already (i.e. if the transaction which
        # had the lock before this one set a 'batch_id' on stock.picking this
        # transaction will not be aware of), we'll probably have a retry. But
        # the lock can help limit the number of retries.
        _logger.info(
            "lock acquired to create a picking batch (%s)", self.env.user.login
        )
