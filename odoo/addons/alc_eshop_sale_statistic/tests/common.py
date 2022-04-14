# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager
from datetime import datetime

import mock
from dateutil import relativedelta
from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestSaleStatistics(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestSaleStatistics, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "product_1",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref("specific_data.product_categ_ali").id,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
                "categ_id": cls.env.ref("specific_data.product_categ_medoc").id,
            }
        )
        cls.partner_1 = cls.env["res.partner"].create({"name": "partner_1"})
        cls.partner_2 = cls.env["res.partner"].create({"name": "partner_2"})
        for month, qties in [
            ("01", [5, 3]),
            ("02", [1, 3]),
            ("03", [5, 3, 1]),
            ("09", [1, 30]),
            ("12", [99, 1, 5, 8]),
        ]:
            for qty in qties:
                cls.sell(cls.product_1, qty, "2020-%s-01 00:00:00" % month)

        # makes sales for top_ordered.... SQL view uses now() ->
        # created sales must be created from now....
        for month_offet, qties in [
            (1, [3]),
            (2, [7]),
            (4, [2]),
            (13, [567]),
        ]:
            for qty in qties:
                date_order = fields.Datetime.to_string(
                    datetime.now() - relativedelta.relativedelta(months=month_offet)
                )
                cls.sell(cls.product_2, qty, date_order)
                cls.sell(cls.product_1, qty / 2, date_order)
        cls.last_date_order = max(
            cls.env["sale.order"]
            .search(
                [
                    ("partner_id", "=", cls.partner_1.id),
                    ("state", "in", ["sale", "done"]),
                ]
            )
            .mapped("date_order")
        )
        cls.env["alc.eshop.product.ordered.qty"].refresh_view()

        cls.sell(cls.product_1, 7, "2015-12-12 00:00:00")  # old data is fine
        cls.sell(cls.product_1, 14, "2018-12-12 00:00:00")
        cls.sell(cls.product_1, 21, "2042-12-12 00:00:00")  # service resist to bad data
        cls.env["alc.eshop.product.ordered.yearly"].refresh_view()

    @classmethod
    def sell(cls, product, qty, ttime, confirm=True, deliver=False):
        with freeze_time(ttime):
            so = cls.env["sale.order"].create(
                {
                    "partner_id": cls.partner_1.id,
                    "sale_channel": "web",
                    "date_order": ttime,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": product.name,
                                "product_id": product.id,
                                "product_uom": product.uom_id.id,
                                "product_uom_qty": qty,
                            },
                        )
                    ],
                }
            )
            if confirm or deliver:
                so.action_confirm()
            if deliver:
                so.picking_ids.action_confirm()
                so.picking_ids.action_done()
        return so

    # pylint: disable=method-required-super
    def setUp(self):
        # resolve an inheritance issue (common.SavepointCase does not call
        # super)
        SavepointCase.setUp(self)
        ComponentMixin.setUp(self)

    @classmethod
    @contextmanager
    def sale_statistics_service(cls, authenticated_partner_id):
        env = cls.env(
            context=dict(
                cls.env.context, authenticated_partner_id=authenticated_partner_id,
            )
        )
        collection = _PseudoCollection("shopinvader.backend", env)
        work = WorkContext(
            model_name="rest.service.registration",
            collection=collection,
            request=mock.Mock(),
            authenticated_partner_id=authenticated_partner_id,
        )
        yield work.component(usage="sale_statistics")
