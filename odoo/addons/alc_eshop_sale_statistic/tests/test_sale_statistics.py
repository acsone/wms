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

    @freeze_time("2020-10-01 00:00:00")
    def test_monthly_ordered(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.monthly_ordered(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 4.333,
                    "months": {
                        "2019-10-01": 0,
                        "2019-11-01": 0,
                        "2019-12-01": 0,
                        "2020-01-01": 8.0,
                        "2020-02-01": 4.0,
                        "2020-03-01": 9.0,
                        "2020-04-01": 0,
                        "2020-05-01": 0,
                        "2020-06-01": 0,
                        "2020-07-01": 0,
                        "2020-08-01": 0,
                        "2020-09-01": 31.0,
                    },
                },
                result,
            )
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_2.id
        ) as service:
            result = service.monthly_ordered(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 0,
                    "months": {
                        "2019-10-01": 0,
                        "2019-11-01": 0,
                        "2019-12-01": 0,
                        "2020-01-01": 0,
                        "2020-02-01": 0,
                        "2020-03-01": 0,
                        "2020-04-01": 0,
                        "2020-05-01": 0,
                        "2020-06-01": 0,
                        "2020-07-01": 0,
                        "2020-08-01": 0,
                        "2020-09-01": 0,
                    },
                },
                result,
            )

    @freeze_time("2020-12-03 00:00:00")
    def test_monthly_ordered_not_current_month(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.monthly_ordered(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 4.333,
                    "months": {
                        "2019-12-01": 0,
                        "2020-01-01": 8.0,
                        "2020-02-01": 4.0,
                        "2020-03-01": 9.0,
                        "2020-04-01": 0,
                        "2020-05-01": 0,
                        "2020-06-01": 0,
                        "2020-07-01": 0,
                        "2020-08-01": 0,
                        "2020-09-01": 31.0,
                        "2020-10-01": 0,
                        "2020-11-01": 0,
                    },
                },
                result,
            )

    def test_top_ordered(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered()
            self.assertTrue(res)
            self.assertEqual(2, res["size"])
            self.assertListEqual(
                res["data"],
                [
                    {
                        "product_family": "meds",
                        "date_last_ordered": service._dt_to_isoformat(
                            self.last_date_order
                        ),
                        "product_id": self.product_2.id,
                        "ordered_count": 12.0,
                    },
                    {
                        "product_family": "food",
                        "date_last_ordered": service._dt_to_isoformat(
                            self.last_date_order
                        ),
                        "product_id": self.product_1.id,
                        "ordered_count": 5.0,
                    },
                ],
            )

    def test_top_ordered_limit(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered(page=1, per_page=1)
            self.assertTrue(res)
            self.assertEqual(2, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_2.id)
            res = service.top_ordered(page=2, per_page=1)
            self.assertEqual(2, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_1.id)

    def test_top_ordered_product_family(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered(product_families=["meds"])
            self.assertEqual(1, res["size"])
            self.assertEqual(1, len(res["data"]))
            self.assertEqual(res["data"][0]["product_id"], self.product_2.id)
            res = service.top_ordered(product_families=["equipment"])
            self.assertEqual(0, res["size"])
            self.assertEqual(0, len(res["data"]))

    def test_top_ordered_discount_only(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            res = service.top_ordered(supplier_discount_only=True)
            self.assertEqual(0, res["size"])
            self.assertEqual(0, len(res["data"]))
