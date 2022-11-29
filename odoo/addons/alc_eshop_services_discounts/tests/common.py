# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager
from datetime import datetime, timedelta

import mock

from odoo.fields import Date
from odoo.tests import SavepointCase

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestDiscountService(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestDiscountService, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()

        vals_partner = {
            "name": "P",
            "partner_type": "veterinary",
            "supplier_promotion_sale_allowed": True,
        }
        cls.partner = cls.env["res.partner"].create(vals_partner)

        product_template = cls.env["product.template"]
        vals_template_meds = {"name": "Meds", "default_code": "MDS14"}
        cls.product_template_meds = product_template.create(vals_template_meds)

        vals_template_food = {"name": "Food", "default_code": "FDS16"}
        cls.product_template_food = product_template.create(vals_template_food)

        cls.now = datetime.now()
        cls.today = Date.to_string(cls.now)

        cls.vendor = cls.env["res.partner"].create({"name": "V", "supplier": True})
        cls.discount_model = cls.env["product.supplierinfo"]

        vals_discount_past = {
            "name": cls.vendor.id,
            "product_tmpl_id": cls.product_template_meds.id,
            "discount_sale": 50,
            "date_start": cls.today_plus(-2),
            "date_end": cls.today_plus(-1),
        }
        cls.discount_past = cls.discount_model.create(vals_discount_past)

        vals_discount_meds = {
            "name": cls.vendor.id,
            "product_tmpl_id": cls.product_template_meds.id,
            "discount_sale": 25,
            "date_start": cls.today,
            "date_end": cls.today_plus(1),
        }
        cls.discount_meds = cls.discount_model.create(vals_discount_meds)

        vals_discount_food = {
            "name": cls.vendor.id,
            "product_tmpl_id": cls.product_template_food.id,
            "date_start": cls.today_plus(1),
            "date_end": cls.today_plus(2),
            "ratio_main_product": 2,
            "ratio_promotional_product": 2,
        }
        cls.discount_food = cls.discount_model.create(vals_discount_food)

        cls.Date = Date

    @classmethod
    def today_plus(cls, days):
        return Date.to_string(cls.now + timedelta(days=days))

    @classmethod
    @contextmanager
    def discount_service(cls, partner):
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
        yield work.component(usage="discounts")
