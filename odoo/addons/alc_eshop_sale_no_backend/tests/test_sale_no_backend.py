# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestSaleNoBackend(CommonCase):
    def setUp(self):
        super(TestSaleNoBackend, self).setUp()
        self.partner = self.env.ref("shopinvader.partner_1")
        with self.work_on_services(partner=self.partner) as work:
            self.service = work.component(usage="sales")

    def test_no_backend_in_domain(self):
        domain = self.service._get_base_search_domain()
        backend_in_domain = (
            len([d for d in domain if d[0] == "shopinvader_backend_id"]) > 0
        )
        self.assertFalse(backend_in_domain)
