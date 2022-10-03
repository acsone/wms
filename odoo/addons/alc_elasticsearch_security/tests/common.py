# coding: utf-8
# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class TestESRoles(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestESRoles, cls).setUpClass()
        ctx = dict(cls.env.context, tracking_disable=True)
        cls.env = cls.env(context=ctx)
        vals_pricelist = {"name": "Bons prixs"}
        cls.pricelist = cls.env["product.pricelist"].create(vals_pricelist)
