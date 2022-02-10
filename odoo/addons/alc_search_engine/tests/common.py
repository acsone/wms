# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.fields import Date

from odoo.addons.alc_supplier_promotion.tests.common import TestSupplierInfo
from odoo.addons.component.tests.common import SavepointComponentCase


class TestExport(TestSupplierInfo, SavepointComponentCase):
    @classmethod
    def setUpClass(cls):
        super(TestExport, cls).setUpClass()
        cls.export = cls.env.ref("shopinvader.ir_exp_shopinvader_variant")

        cls.in_two_days = Date.to_string(Date.from_string(cls.tomorrow) + cls.one_day)

        cls.backend = cls.env.ref("shopinvader.backend_1")
        cls.backend.bind_all_product(domain=[("id", "=", cls.product_template.id)])
