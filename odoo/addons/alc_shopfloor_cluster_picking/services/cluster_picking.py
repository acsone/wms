# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo.osv import expression

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class ClusterPicking(Component):
    _inherit = "shopfloor.cluster.picking"

    def find_existing_batch(self):
        batches = self._batch_picking_search()
        if batches:
            selected = self._select_a_picking_batch(batches)
            return self._response_for_confirm_start(selected)
        return self._response_for_start()

    def _select_a_picking_batch(self, batches):
        batch = super(ClusterPicking, self)._select_a_picking_batch(batches)
        if not batch and self.work.menu.batch_create:
            batch = self._batch_auto_create()
            if batch:
                batch.assign_operator(operator=self.shopfloor_user)
                batch.state = "in_progress"
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

    @property
    def _advisory_lock_name(self):
        return ",".join(self.work.menu.picking_type_ids.mapped("name"))

    def _lock(self):
        """Lock to prevent concurrent creation of batch
        Use a blocking advisory lock to prevent 2 transactions to create
        a batch at the same time. The lock is released at the commit or
        rollback of the transaction.
        The creation of a new batch should be short enough not to block
        the users for too long.
        """
        _logger.info(
            "trying to acquire lock to create a picking batch (%s)",
            self.shopfloor_user.name,
        )
        self.work.menu.picking_type_ids.lock()
        # Note: if the lock had to wait, the snapshot of the transaction is
        # very much probably outdated already (i.e. if the transaction which
        # had the lock before this one set a 'batch_id' on stock.picking this
        # transaction will not be aware of), we'll probably have a retry. But
        # the lock can help limit the number of retries.
        _logger.info(
            "lock acquired to create a picking batch (%s)", self.env.user.login
        )


class ShopfloorClusterPickingValidatorResponse(Component):
    """Validators for the Cluster Picking endpoints responses"""

    _inherit = "shopfloor.cluster_picking.validator.response"

    def find_existing_batch(self):
        return self._response_schema(next_states={"start", "confirm_start"})


class ShopfloorClusterPickingValidator(Component):
    """Validators for the Cluster Picking endpoints"""

    _inherit = "shopfloor.cluster_picking.validator"

    def find_existing_batch(self):
        return {}
