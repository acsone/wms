# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if not version:
        return

    _logger.info("Set customer on procurement group for procurement linked to SO")

    cr.execute(
        "Update procurement_group set customer_id = partner_id where name like 'SO%' "
    )

    _logger.info("Set customer on pickings for pickings linked to SO")

    cr.execute(
        """
        UPDATE
            stock_picking
        SET
            customer_id = partner_id
        FROM
            stock_picking_type st
        WHERE
            stock_picking.picking_type_id = st.id
            AND (
                st.subcode in ('PICK')
                OR
                st.name = 'Delivery Orders'
            )
        """
    )
