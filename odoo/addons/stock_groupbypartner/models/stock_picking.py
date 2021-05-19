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

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        help="The partner customer on the SO if the picking has been created "
        "for a procurement group linked to a SO.",
        index=True,
    )

    @api.model_cr
    def init(self):
        # create index for the domain expressed into the
        # stock_move._assign_picking_group_domain method
        index_name = "stock_picking_groupbypartner_key_index"
        self.env.cr.execute(
            "SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,)
        )
        if not self.env.cr.fetchone():
            self.env.cr.execute(
                """
        CREATE INDEX %s
        ON %s (customer_id, partner_id, location_id, location_dest_id, picking_type_id)
        WHERE
            printed is false
            AND state not in ('draft', 'cancel', 'done')
                """,
                (AsIs(index_name), AsIs(self._table)),
            )

    def _lock(self):
        """Lock the database rows of the picking to prevent concurrent access.

        The lock is released when the transaction is committed or rolled back.

        This method is called:
        1. when adding a move in the picking to prevent the picking to be started
        2. when detaching the picking from delivery round (no_new_picking)
        3. when assigning the picking to a delivery round to prevent new moves to be added
        """
        if self:
            _logger.info("acquire lock for pickings %s", self.ids)
            self.env.cr.execute(
                "SELECT printed FROM stock_picking WHERE id in %s FOR UPDATE",
                (tuple(self.ids),),
            )
            _logger.info("lock acquired for pickings %s", self.ids)

    @api.multi
    def _create_backorder(self, backorder_moves=None):
        """ Take care of grouping by partner.
        Reuse the overriden method action_assign that search a good picking or
        create a new one.
        Apply this to all non-done lines into an existing for a new backorder
        picking. If the key 'do_only_split' is given in the context, then move
        all lines not in context.get('split', []) instead of all non-done
        lines.
        Pay attention to unsafe standard signature "backorder_moves=[]".
        """
        backorders = self.env["stock.picking"]

        picking_togroup = self.filtered(lambda p: p.picking_type_id.groupbypartner)
        picking_notgroup = self - picking_togroup

        for picking in picking_togroup:
            if self._context.get("do_only_split"):
                not_done_bo_moves = picking.move_lines.filtered(
                    lambda move: move.id not in self._context.get("split", [])
                )
            else:
                not_done_bo_moves = picking.move_lines.filtered(
                    lambda move: move.state not in ("done", "cancel")
                )

            if backorder_moves:
                not_done_bo_moves = backorder_moves.filtered(
                    lambda m, dm=not_done_bo_moves: m in dm
                )

            if not not_done_bo_moves:
                continue

            if not picking.printed:
                # Mark delivery as processed. When reassigning move in
                # backorder, we look for picking not printed
                picking.printed = True

            if self.env.context.get("cancel_backorder"):
                # Triggerred by delivery round shipping delivery
                # for partner that does not accept backorder
                not_done_bo_moves.with_context(
                    no_recompute_pack=True, force_cancel=True
                ).action_cancel()
                picking.message_post(
                    body=_(
                        "Remaining moves canceled as partner does not "
                        "accept backorder:<ul>%s</ul>"
                    )
                    % "".join(
                        ["<li>%s</li>" % m for m in not_done_bo_moves.mapped("name")]
                    )
                )

                def key(r):
                    return r.picking_id

                cancel_moves = (
                    not_done_bo_moves.filtered(lambda move: move.propagate)
                    .mapped("move_orig_ids")
                    .filtered(lambda move: move.state not in ("cancel", "done"))
                    .sorted(key=key)
                )
                # Propagate to picking
                for cancel_picking, cancel_moves_iter in groupby(cancel_moves, key=key):
                    cancel_moves_bypicking = reduce(
                        lambda x, y: x | y, cancel_moves_iter
                    )
                    cancel_moves_bypicking.with_context(
                        no_recompute_pack=True, force_cancel=True
                    ).action_cancel()
                    cancel_picking.message_post(
                        body=_(
                            "Remaining moves canceled as partner does not "
                            "accept backorder:<ul>%s</ul>"
                        )
                        % "".join(
                            [
                                "<li>%s</li>" % m
                                for m in cancel_moves_bypicking.mapped("name")
                            ]
                        )
                    )

            else:
                not_done_bo_moves.assign_picking()

            # In the call to assign_picking, additional products have been
            # canceled.
            not_done_bo_moves = not_done_bo_moves.filtered(
                # we need to check if the move exists because we can have
                # deleted moves in case of additional products
                lambda move: move.exists()
                and move.state not in ("done", "cancel")
            )
            if (
                picking not in not_done_bo_moves.mapped("picking_id")
                and not picking.date_done
            ):
                # Only set date_done if the original picking is no more linked to the
                # moves to do
                picking.write(
                    {"date_done": time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)}
                )
            backorders |= not_done_bo_moves.mapped("picking_id")
        if backorders:
            # In standard, created backorders are assigned at the end of the
            # method
            backorders.action_assign()

        for picking in picking_notgroup:
            # Do not call _create_backorder on recordset due to unsafe
            # signature "backorder_moves=[]" and ensure backorder_moves is
            # correctly set
            bm = None
            if backorder_moves:
                bm = backorder_moves.filtered(lambda m, p=picking: m.picking_id == p)
                if not bm:
                    continue
            backorders |= super(StockPicking, picking)._create_backorder(
                backorder_moves=bm
            )

        return backorders
