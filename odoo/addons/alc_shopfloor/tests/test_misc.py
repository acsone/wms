# -*- coding: utf-8 -*-
# Copyright 2020 Camptocamp SA (http://www.camptocamp.com)
# Copyright 2021 ACSONE SA/NV (https://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import exceptions
from odoo.tests.common import SavepointCase


class MiscTestCase(SavepointCase):
    tracking_disable = True

    @classmethod
    def setUpClass(cls):
        super(MiscTestCase, cls).setUpClass()
        cls.env = cls.env(
            context=dict(cls.env.context, tracking_disable=cls.tracking_disable)
        )

    def test_package_name_unique(self):
        create = self.env["stock.quant.package"].create
        create({"name": "GOOD_NAME"})
        with self.assertRaises(exceptions.ValidationError) as exc:
            create({"name": "GOOD_NAME"})
        self.assertEqual(exc.exception.name, "Package name must be unique!")
