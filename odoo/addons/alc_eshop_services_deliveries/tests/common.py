# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock

from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestDeliveriesService(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestDeliveriesService, cls).setUpClass()
        cls.setUpComponent()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.product_ship = cls.env["product.product"].create(
            {"name": "Shipit", "default_code": "SHP"}
        )
        cls.product_cancel = cls.env["product.product"].create(
            {"name": "Cancel", "default_code": "CNL"}
        )

        cls.location_customer = cls.env.ref("stock.stock_location_customers")
        cls.location_stock = cls.env.ref("stock.stock_location_stock")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")

        moves_picking_cancel = [(cls.product_cancel, 1)]
        moves_picking_done = [(cls.product_ship, 1)]
        cls.picking_cancel = cls.create_picking(moves_picking_cancel)
        cls.picking_half = cls.create_picking(moves_picking_cancel + moves_picking_done)
        cls.picking_done = cls.create_picking(moves_picking_done)

        cls.picking_cancel.with_context(force_cancel=True).action_cancel()
        # picking_half: cancel half of it, deliver the rest
        filter_move = lambda m: m.product_id == cls.product_cancel
        cls.move_done_cancel = cls.picking_half.move_lines.filtered(filter_move)
        cls.move_done_cancel.state = "cancel"
        cls.picking_half.action_confirm()
        cls.picking_half.force_assign()
        cls.picking_half.action_done()

        cls.picking_done.action_confirm()
        cls.picking_done.force_assign()
        cls.picking_done.action_done()

    @classmethod
    @contextmanager
    def service(cls, partner=None):
        # this is once again pasted, so should go into a ServiceCase class
        partner_id = (partner or cls.partner).id
        context = dict(cls.env.context, authenticated_partner_id=partner_id)
        env = cls.env(context=context)
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=partner_id,
        )
        yield work.component(usage="pickings")

    @classmethod
    def create_picking(cls, move_tuples, partner=None):
        moves = []
        for product, qty in move_tuples:
            move = {
                "name": "{} {}".format(product.name, qty),
                "product_id": product.id,
                "product_uom_qty": qty,
                "product_uom": product.uom_id.id,
                "location_id": cls.location_stock,
                "location_dest_id": cls.location_customer,
            }
            moves.append((0, 0, move))
        vals = {
            "picking_type_id": cls.picking_type_out.id,
            "location_id": cls.location_stock.id,
            "location_dest_id": cls.location_customer.id,
            "partner_id": (partner or cls.partner).id,
            "customer_id": (partner or cls.partner).id,
            "move_lines": moves,
        }
        return cls.env["stock.picking"].create(vals)
