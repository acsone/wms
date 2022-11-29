# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_product_flattened_data.tests.common import TestProductFlattenedData
from odoo.addons.component.tests.common import ComponentMixin

from .. import facade


class TestFacade(TestProductFlattenedData, ComponentMixin):
    @classmethod
    def setUpClass(cls):
        super(TestFacade, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.setUpComponent()

        vals_partner = {"name": "P", "partner_type": "veterinary"}
        cls.partner = cls.env["res.partner"].create(vals_partner)

    def _get_service_facade(self, service):
        return facade.Facade.factory(self.env, self.partner, service)
