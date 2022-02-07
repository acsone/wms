# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo.fields import Date
from odoo.tests.common import SavepointCase


class TestSupplierInfo(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSupplierInfo, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.vendor = cls.env["res.partner"].create({"name": "V"})
        cls.product_template = cls.env["product.template"].create({"name": "P"})
        cls.product = cls.product_template.product_variant_id
        cls.today = Date.context_today(cls.product_template)
        today = Date.from_string(cls.today)
        cls.one_day = datetime.timedelta(days=1)
        yesterday = today - cls.one_day
        cls.yesterday = Date.to_string(yesterday)
        cls.tomorrow = Date.to_string(today + cls.one_day)

        cls.supplierinfo_model = cls.env["product.supplierinfo"]

    def get_supplierinfo_vals(self, **kwargs):
        defaults = {
            "name": self.vendor.id,
            "price": 10,
            "product_id": self.product.id,
            "product_tmpl_id": self.product_template.id,
        }
        return dict(defaults, **kwargs)
