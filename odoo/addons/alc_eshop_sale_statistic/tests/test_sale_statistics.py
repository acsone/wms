# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from contextlib import contextmanager

import mock
from freezegun import freeze_time

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
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "product_2",
                "uom_id": cls.env.ref("product.product_uom_unit").id,
                "type": "product",
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
                cls.sell(cls.product_1, qty, "2022-%s-01 00:00:00" % month)

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

    @freeze_time("2022-10-01 00:00:00")
    def test_monthly_purchased(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.monthly_purchased(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 4.333,
                    "months": {
                        "2021-10-01": 0,
                        "2021-11-01": 0,
                        "2021-12-01": 0,
                        "2022-01-01": 8.0,
                        "2022-02-01": 4.0,
                        "2022-03-01": 9.0,
                        "2022-04-01": 0,
                        "2022-05-01": 0,
                        "2022-06-01": 0,
                        "2022-07-01": 0,
                        "2022-08-01": 0,
                        "2022-09-01": 31.0,
                    },
                },
                result,
            )
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_2.id
        ) as service:
            result = service.monthly_purchased(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 0,
                    "months": {
                        "2021-10-01": 0,
                        "2021-11-01": 0,
                        "2021-12-01": 0,
                        "2022-01-01": 0,
                        "2022-02-01": 0,
                        "2022-03-01": 0,
                        "2022-04-01": 0,
                        "2022-05-01": 0,
                        "2022-06-01": 0,
                        "2022-07-01": 0,
                        "2022-08-01": 0,
                        "2022-09-01": 0,
                    },
                },
                result,
            )

    @freeze_time("2022-12-03 00:00:00")
    def test_monthly_purchased_not_current_month(self):
        with self.sale_statistics_service(
            authenticated_partner_id=self.partner_1.id
        ) as service:
            result = service.monthly_purchased(product_id=self.product_1.id)
            self.assertDictEqual(
                {
                    "average": 4.333,
                    "months": {
                        "2021-12-01": 0,
                        "2022-01-01": 8.0,
                        "2022-02-01": 4.0,
                        "2022-03-01": 9.0,
                        "2022-04-01": 0,
                        "2022-05-01": 0,
                        "2022-06-01": 0,
                        "2022-07-01": 0,
                        "2022-08-01": 0,
                        "2022-09-01": 31.0,
                        "2022-10-01": 0,
                        "2022-11-01": 0,
                    },
                },
                result,
            )
