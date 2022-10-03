# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

import mock

from odoo.tests import SavepointCase

from odoo.addons.alc_product_flattened_data.tests.common import TestProductFlattenedData
from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext
from odoo.addons.component.tests.common import ComponentMixin


class TestBrandsService(SavepointCase, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestBrandsService, cls).setUpClass()
        cls.setUpComponent()

        cls.partner = cls.env["res.partner"].create({"name": "P"})
        cls.brand_1 = cls.env["product.brand"].create({"name": "numbah 1"})
        cls.brand_2 = cls.env["product.brand"].create({"name": "numéro 2"})

    @classmethod
    @contextmanager
    def brands_service(cls, partner):
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
        yield work.component(usage="brands")


class TestCatalogService(TestProductFlattenedData, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestCatalogService, cls).setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()

        vals_partner = {"name": "P", "partner_type": "veterinary"}
        cls.partner = cls.env["res.partner"].create(vals_partner)

    @classmethod
    @contextmanager
    def catalog_service(cls, partner):
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
        yield work.component(usage="catalog")
